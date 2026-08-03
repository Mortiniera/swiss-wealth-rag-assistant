"""Out-of-scope response node (no retrieval)."""

from __future__ import annotations

from app.agent.intent import build_out_of_scope_response
from app.agent.state import AgentState


def run(state: AgentState) -> None:
    """Return the fixed out-of-scope refusal."""
    result = build_out_of_scope_response()
    state.answer = result["answer"]
    state.sources = result.get("sources") or []
    state.status = "completed"
