"""Bounded workflow runner for /ask (explicit steps, hard max iterations)."""

from __future__ import annotations

import logging
from collections.abc import Callable

from app.agent import nodes
from app.agent.routing import (
    END,
    STEP_CLASSIFY,
    STEP_GENERATE,
    STEP_RESPOND_META,
    STEP_RESPOND_OOS,
    STEP_REWRITE,
    next_step,
)
from app.agent.state import AgentState
from app.models.schemas import ChatMessage

logger = logging.getLogger(__name__)

MAX_HISTORY_TURNS = 10
MAX_STEPS = 8

CONTROLLED_FAILURE = {
    "answer": (
        "I could not complete this request within the allowed workflow steps. "
        "Please try again or rephrase your question."
    ),
    "sources": [],
}

NodeFn = Callable[[AgentState], None]

NODES: dict[str, NodeFn] = {
    STEP_CLASSIFY: nodes.classify,
    STEP_REWRITE: nodes.rewrite,
    STEP_GENERATE: nodes.generate,
    STEP_RESPOND_META: nodes.respond_meta,
    STEP_RESPOND_OOS: nodes.respond_oos,
}


def _finalize(state: AgentState) -> dict:
    """Map terminal state to the /ask response dict."""
    if state.status == "completed" and state.answer is not None:
        return {"answer": state.answer, "sources": state.sources}
    state.status = "failed"
    if state.error is None:
        state.error = "Workflow ended without a completed answer"
    logger.warning(
        "Agent workflow failed: error=%s transitions=%s",
        state.error,
        state.transitions,
    )
    return dict(CONTROLLED_FAILURE)


def handle_question(
    question: str,
    history: list[ChatMessage] | None = None,
    *,
    role: str | None = None,
) -> dict:
    """
    Run the bounded agent workflow for one question.

    Public contract matches the previous linear orchestrator: ``{answer, sources}``.
    """
    state = AgentState(
        question=question,
        history=(history or [])[-MAX_HISTORY_TURNS:],
        role=role,
    )

    for _ in range(MAX_STEPS):
        nxt = next_step(state)
        if nxt == END:
            break

        node = NODES.get(nxt)
        if node is None:
            state.status = "failed"
            state.error = f"Unknown workflow step '{nxt}'"
            break

        state.transitions.append(nxt)
        state.step = nxt
        node(state)

        if state.status in ("completed", "failed"):
            break
    else:
        # Loop exhausted without break, hard bound hit after max steps.
        state.status = "failed"
        state.error = f"Exceeded MAX_STEPS ({MAX_STEPS})"

    logger.info(
        "Agent workflow finished: status=%s transitions=%s",
        state.status,
        state.transitions,
    )
    return _finalize(state)
