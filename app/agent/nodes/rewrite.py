"""Query rewrite node."""

from __future__ import annotations

from app.agent.query_rewriter import rewrite_query
from app.agent.state import AgentState


def run(state: AgentState) -> None:
    """Rewrite the question with conversation context for retrieval."""
    state.rewritten_query = rewrite_query(state.question, state.history)
