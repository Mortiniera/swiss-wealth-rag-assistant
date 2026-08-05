"""Langfuse client lifecycle: init once at startup, no-op without keys."""

from __future__ import annotations

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

_client: Any | None = None
_enabled: bool = False


def _normalize(value: str) -> str:
    return (value or "").strip().strip('"').strip("'")


def _credentials_configured(public_key: str, secret_key: str) -> bool:
    """True when both keys look set (not empty / not .env.example placeholders)."""
    if not public_key or not secret_key:
        return False
    if public_key.upper().startswith("YOUR_") or secret_key.upper().startswith("YOUR_"):
        return False
    return True


def is_enabled() -> bool:
    return _enabled


def get_client() -> Any | None:
    """Return the Langfuse client when tracing is enabled, else None."""
    return _client if _enabled else None


def reset_observability() -> None:
    """Clear module state (tests)."""
    global _client, _enabled
    _client = None
    _enabled = False


def init_observability() -> bool:
    """
    Initialize Langfuse when public + secret keys are present.

    Never raises: failures leave tracing disabled so the API keeps working.
    Returns True when tracing is enabled after this call.
    """
    global _client, _enabled

    reset_observability()

    public_key = _normalize(settings.langfuse_public_key)
    secret_key = _normalize(settings.langfuse_secret_key)
    base_url = _normalize(settings.langfuse_base_url)

    if not _credentials_configured(public_key, secret_key):
        logger.info("Langfuse tracing disabled (LANGFUSE_PUBLIC_KEY/SECRET_KEY not set)")
        return False

    try:
        from langfuse import Langfuse

        kwargs: dict[str, str] = {
            "public_key": public_key,
            "secret_key": secret_key,
        }
        if base_url:
            kwargs["base_url"] = base_url

        _client = Langfuse(**kwargs)
        _enabled = True
        logger.info(
            "Langfuse tracing enabled (base_url=%s)",
            base_url or "https://cloud.langfuse.com",
        )
        return True
    except Exception:
        logger.exception(
            "Langfuse init failed; continuing with tracing disabled"
        )
        reset_observability()
        return False
