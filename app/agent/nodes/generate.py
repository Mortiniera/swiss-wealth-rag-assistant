"""Grounded generation node."""

from __future__ import annotations

from app.agent.state import AgentState
from app.rag.generator import generate_answer


def run(state: AgentState) -> None:
    """Run hybrid retrieval + grounded generation."""
    result = generate_answer(
        state.question,
        history=state.history,
        rewritten_query=state.rewritten_query,
        role=state.role,
    )
    state.answer = result["answer"]
    state.sources = result.get("sources") or []
    state.status = "completed"
