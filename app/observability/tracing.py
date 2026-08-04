"""No-op-safe span helpers for /ask tracing."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from app.observability.langfuse_client import get_client

logger = logging.getLogger(__name__)

# Langfuse observation types for workflow steps
_STEP_AS_TYPE: dict[str, str] = {
    "ask": "chain",
    "agent_turn": "agent",
    "run_tools": "tool",
    "search_policies": "retriever",
}


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
