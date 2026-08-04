"""Opt-in observability (Langfuse). Missing keys → no-op."""

from app.observability.langfuse_client import (
    get_client,
    init_observability,
    is_enabled,
    reset_observability,
)
from app.observability.tracing import (
    current_trace_id,
    flush_observability,
    observe,
    safe_update,
)

__all__ = [
    "current_trace_id",
    "flush_observability",
    "get_client",
    "init_observability",
    "is_enabled",
    "observe",
    "reset_observability",
    "safe_update",
]
