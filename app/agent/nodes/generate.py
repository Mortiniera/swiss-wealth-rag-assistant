"""Grounded generation node."""

from __future__ import annotations

from app.agent.facts import format_structured_facts
from app.agent.state import AgentState
from app.rag.generator import generate_answer


def run(state: AgentState) -> None:
    """Run hybrid retrieval + grounded generation (with optional tool facts)."""
    policy_chunks = state.policy_hits if state.policy_queries else None
    result = generate_answer(
        state.question,
        history=state.history,
        rewritten_query=state.rewritten_query,
        role=state.role,
        structured_facts=format_structured_facts(state.tool_results),
        policy_chunks=policy_chunks,
    )
    state.answer = result["answer"]
    state.sources = result.get("sources") or []
    state.status = "completed"
