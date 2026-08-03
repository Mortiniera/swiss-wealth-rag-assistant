"""Assistant-meta response node (no retrieval)."""

from __future__ import annotations

from app.agent.intent import build_meta_response
from app.agent.state import AgentState


def run(state: AgentState) -> None:
    """Return the fixed assistant capability response."""
    result = build_meta_response(state.question, state.history)
    state.answer = result["answer"]
    state.sources = result.get("sources") or []
    state.status = "completed"
