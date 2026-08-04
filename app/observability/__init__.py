"""Opt-in observability (Langfuse). Missing keys → no-op."""

from app.observability.langfuse_client import (
    get_client,
    init_observability,
    is_enabled,
    reset_observability,
)

__all__ = [
    "get_client",
    "init_observability",
    "is_enabled",
    "reset_observability",
]
