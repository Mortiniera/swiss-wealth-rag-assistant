"""No-op-safe span helpers for /ask tracing."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from app.config import settings
from app.observability.langfuse_client import get_client

logger = logging.getLogger(__name__)

# Langfuse observation types for workflow steps.
_STEP_AS_TYPE: dict[str, str] = {
    "ask": "chain",
    "agent_turn": "agent",
    "run_tools": "tool",
    "search_policies": "retriever",
}


def extract_usage_details(response: Any) -> dict[str, int] | None:
    """Best-effort token usage from a LlamaIndex completion response."""
    raw = getattr(response, "raw", None)
    usage_obj = getattr(raw, "usage", None) if raw is not None else None
    if usage_obj is None and isinstance(raw, dict):
        usage_obj = raw.get("usage")

    if usage_obj is None:
        extra = getattr(response, "additional_kwargs", None) or {}
        usage_obj = extra.get("usage") if isinstance(extra, dict) else None

    if usage_obj is None:
        return None

    if isinstance(usage_obj, dict):
        prompt = usage_obj.get("prompt_tokens") or usage_obj.get("input_tokens")
        completion = usage_obj.get("completion_tokens") or usage_obj.get("output_tokens")
        total = usage_obj.get("total_tokens")
    else:
        prompt = getattr(usage_obj, "prompt_tokens", None) or getattr(
            usage_obj, "input_tokens", None
        )
        completion = getattr(usage_obj, "completion_tokens", None) or getattr(
            usage_obj, "output_tokens", None
        )
        total = getattr(usage_obj, "total_tokens", None)

    details: dict[str, int] = {}
    if prompt is not None:
        details["input"] = int(prompt)
    if completion is not None:
        details["output"] = int(completion)
    if total is not None:
        details["total"] = int(total)
    return details or None


@contextmanager
def observe(
    name: str,
    *,
    metadata: dict[str, Any] | None = None,
    as_type: str | None = None,
) -> Iterator[Any | None]:
    """
    Open a Langfuse observation when tracing is enabled; otherwise yield None.

    Failures creating the span are logged and become no-ops. Exceptions from the
    wrapped body still propagate.
    """
    client = get_client()
    if client is None:
        yield None
        return

    obs_type = as_type or _STEP_AS_TYPE.get(name, "span")
    try:
        cm = client.start_as_current_observation(
            name=name,
            as_type=obs_type,
            metadata=metadata or None,
        )
    except Exception:
        logger.exception("Langfuse observe(%s) failed; continuing without span", name)
        yield None
        return

    with cm as span:
        yield span


@contextmanager
def observe_generation(
    name: str,
    *,
    prompt_length: int,
    model: str | None = None,
) -> Iterator[Any | None]:
    """Open a Langfuse generation observation for an LLM call."""
    llm_model = model or settings.llm_model
    with observe(
        name,
        as_type="generation",
        metadata={"prompt_length": prompt_length, "model": llm_model},
    ) as span:
        if span is not None:
            safe_update(span, model=llm_model)
        yield span


def finish_generation(
    span: Any | None,
    response: Any,
    *,
    elapsed_s: float,
    prompt_length: int,
    output_max_len: int = 120,
) -> None:
    """Record LLM completion metadata on a generation span (no full prompt body)."""
    text = (getattr(response, "text", None) or "").strip()
    meta: dict[str, Any] = {
        "latency_s": round(elapsed_s, 3),
        "prompt_length": prompt_length,
        "completion_length": len(text),
    }
    kwargs: dict[str, Any] = {"metadata": meta}
    if text:
        kwargs["output"] = text[:output_max_len]
    usage = extract_usage_details(response)
    if usage:
        kwargs["usage_details"] = usage
    safe_update(span, **kwargs)


def current_trace_id() -> str | None:
    """Return the active Langfuse trace id, if any."""
    client = get_client()
    if client is None:
        return None
    try:
        return client.get_current_trace_id()
    except Exception:
        logger.exception("Failed to read Langfuse trace id")
        return None


def flush_observability() -> None:
    """Flush pending Langfuse events (no-op when disabled)."""
    client = get_client()
    if client is None:
        return
    try:
        client.flush()
    except Exception:
        logger.exception("Langfuse flush failed")


def safe_update(span: Any | None, **kwargs: Any) -> None:
    """Update a span when present; swallow errors."""
    if span is None:
        return
    try:
        span.update(**kwargs)
    except Exception:
        logger.exception("Langfuse span.update failed")
