"""Opt-in observability (Langfuse). Missing keys → no-op."""

from app.observability.langfuse_client import (
    get_client,
    init_observability,
    is_enabled,
    reset_observability,
)
from app.observability.tracing import (
    current_trace_id,
    extract_usage_details,
    finish_generation,
    flush_observability,
    observe,
    observe_generation,
    safe_update,
)

__all__ = [
    "current_trace_id",
    "extract_usage_details",
    "finish_generation",
    "flush_observability",
    "get_client",
    "init_observability",
    "is_enabled",
    "observe",
    "observe_generation",
    "reset_observability",
    "safe_update",
]
