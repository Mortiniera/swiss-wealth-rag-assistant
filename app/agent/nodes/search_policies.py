"""Hybrid policy retrieval as an explicit agent turn (search_policies action)."""

from __future__ import annotations

import logging

from app.agent.state import AgentState
from app.database.session import SessionLocal
from app.rag.generator import _hit_to_chunk
from app.retrieval import RetrievalFilters, retrieve as retrieve_policies

logger = logging.getLogger(__name__)


def _merge_policy_hits(state: AgentState, new_chunks: list[dict]) -> int:
    """Append unique chunks by chunk_id; return count added."""
    seen = {row.get("chunk_id") for row in state.policy_hits}
    added = 0
    for chunk in new_chunks:
        chunk_id = chunk.get("chunk_id")
        if not chunk_id or chunk_id in seen:
            continue
        seen.add(chunk_id)
        state.policy_hits.append(chunk)
        added += 1
    return added


def run(state: AgentState) -> None:
    """Run one policy search for the current turn and record observations."""
    query = (state.policy_query or state.question).strip()
    if not query:
        return

    session = SessionLocal()
    try:
        hits = retrieve_policies(
            session,
            query,
            filters=RetrievalFilters(status="active", role=state.role),
        )
    finally:
        session.close()

    chunks = [_hit_to_chunk(hit) for hit in hits]
    added = _merge_policy_hits(state, chunks)
    state.policy_queries.append(query)
    state.policy_query = None
    state.tool_round += 1
    state.round_trace.append(
        {
            "round": state.tool_round,
            "decision": state.last_decision,
            "selected": [],
            "policy_query": query,
            "policy_hits": len(chunks),
            "policy_hits_new": added,
        }
    )

    if state.tool_round >= state.max_tool_rounds:
        state.stop_reason = "max_tool_rounds"

    logger.info(
        "Policy search round %s: query=%r hits=%d new=%d stop_reason=%s",
        state.tool_round,
        query[:80],
        len(chunks),
        added,
        state.stop_reason,
    )
