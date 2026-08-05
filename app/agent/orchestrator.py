"""Bounded workflow runner for /ask (explicit steps, hard max iterations)."""

from __future__ import annotations

import logging
from collections.abc import Callable

from app.agent import nodes
from app.agent.client_ref import extract_client_ref
from app.agent.facts import evidence_from_tool_results
from app.agent.routing import (
    END,
    STEP_AGENT_TURN,
    STEP_CLASSIFY,
    STEP_GENERATE,
    STEP_RESPOND_META,
    STEP_RESPOND_OOS,
    STEP_REWRITE,
    STEP_RUN_TOOLS,
    STEP_SEARCH_POLICIES,
    next_step,
)
from app.agent.state import AgentState
from app.models.schemas import ChatMessage
from app.observability.tracing import (
    current_trace_id,
    dev_trace_url,
    flush_observability,
    observe,
    safe_update,
)

logger = logging.getLogger(__name__)

MAX_HISTORY_TURNS = 10
# classify + up to 5×(turn+run) + finish turn + rewrite + generate.
MAX_STEPS = 18

CONTROLLED_FAILURE = {
    "answer": (
        "I could not complete this request within the allowed workflow steps. "
        "Please try again or rephrase your question."
    ),
    "sources": [],
    "evidence": [],
}

NodeFn = Callable[[AgentState], None]

NODES: dict[str, NodeFn] = {
    STEP_CLASSIFY: nodes.classify,
    STEP_AGENT_TURN: nodes.agent_turn,
    STEP_RUN_TOOLS: nodes.run_tools,
    STEP_SEARCH_POLICIES: nodes.search_policies,
    STEP_REWRITE: nodes.rewrite,
    STEP_GENERATE: nodes.generate,
    STEP_RESPOND_META: nodes.respond_meta,
    STEP_RESPOND_OOS: nodes.respond_oos,
}


def _finalize(state: AgentState) -> dict:
    """Map terminal state to the /ask response dict."""
    evidence = evidence_from_tool_results(state.tool_results)
    if state.status == "completed" and state.answer is not None:
        return {
            "answer": state.answer,
            "sources": state.sources,
            "evidence": evidence,
        }
    state.status = "failed"
    if state.error is None:
        state.error = "Workflow ended without a completed answer"
    logger.warning(
        "Agent workflow failed: error=%s transitions=%s",
        state.error,
        state.transitions,
    )
    return dict(CONTROLLED_FAILURE)


def _ask_root_metadata(
    *,
    role: str | None,
    actor_employee_code: str | None,
    question: str,
    history_turns: int,
) -> dict:
    """Codes-only attributes for the root /ask span (no emails/names/question body)."""
    return {
        "role": role,
        "actor_employee_code": actor_employee_code,
        "question_length": len(question),
        "history_turns": history_turns,
    }


def _finalize_ask_span(span, state: AgentState) -> None:
    safe_update(
        span,
        metadata={
            "client_ref": state.client_ref,
            "intent": state.intent,
            "stop_reason": state.stop_reason,
            "tool_round": state.tool_round,
            "status": state.status,
            "transitions": list(state.transitions),
        },
        output={"status": state.status, "stop_reason": state.stop_reason},
        level="ERROR" if state.status == "failed" else "DEFAULT",
        status_message=state.error if state.status == "failed" else None,
    )


def _run_node_with_span(step: str, node: NodeFn, state: AgentState) -> None:
    """Execute one workflow node under a child observation."""
    meta: dict = {"step": step}
    if step == STEP_RUN_TOOLS and state.selected_tools:
        meta["tools"] = list(state.selected_tools)
        meta["tool_round_before"] = state.tool_round
    if step == STEP_SEARCH_POLICIES and state.policy_query:
        meta["policy_query"] = state.policy_query

    with observe(step, metadata=meta) as span:
        node(state)
        if step == STEP_CLASSIFY:
            safe_update(span, metadata={"intent": state.intent})
        elif step == STEP_RUN_TOOLS:
            safe_update(
                span,
                metadata={
                    "tool_round": state.tool_round,
                    "selected_tools": list(state.selected_tools),
                },
            )
        elif step == STEP_SEARCH_POLICIES:
            last_round = state.round_trace[-1] if state.round_trace else {}
            round_scores = [
                hit.get("score")
                for hit in state.policy_hits
                if hit.get("score") is not None
            ]
            safe_update(
                span,
                metadata={
                    "policy_hit_count": len(state.policy_hits),
                    "hits_this_round": last_round.get("policy_hits"),
                    "hits_added": last_round.get("policy_hits_new"),
                    "top_score": max(round_scores) if round_scores else None,
                    "query_length": len(last_round.get("policy_query") or ""),
                },
            )
        elif step == STEP_AGENT_TURN and state.last_decision:
            decision = state.last_decision
            safe_update(
                span,
                metadata={
                    "action": decision.get("action"),
                    "tool": decision.get("tool"),
                    "reason_code": decision.get("reason_code"),
                },
            )


def handle_question(
    question: str,
    history: list[ChatMessage] | None = None,
    *,
    role: str | None = None,
    actor_employee_code: str | None = None,
) -> dict:
    """
    Run the bounded agent workflow for one question.

    Public contract: ``{answer, sources}``. Optional Act-as identity scopes tools.
    """
    history_turns = len(history or [])
    root_meta = _ask_root_metadata(
        role=role,
        actor_employee_code=actor_employee_code,
        question=question,
        history_turns=history_turns,
    )

    with observe("ask", metadata=root_meta) as ask_span:
        state = AgentState(
            question=question,
            history=(history or [])[-MAX_HISTORY_TURNS:],
            role=role,
            actor_employee_code=actor_employee_code,
            client_ref=extract_client_ref(question),
        )
        safe_update(ask_span, metadata={"client_ref": state.client_ref})

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
            _run_node_with_span(nxt, node, state)

            if state.status in ("completed", "failed"):
                break
        else:
            # Loop exhausted without break, hard bound hit after max steps.
            state.status = "failed"
            state.error = f"Exceeded MAX_STEPS ({MAX_STEPS})"

        _finalize_ask_span(ask_span, state)

        logger.info(
            "Agent workflow finished: status=%s client_ref=%s tool_round=%s "
            "stop_reason=%s transitions=%s trace_id=%s",
            state.status,
            state.client_ref,
            state.tool_round,
            state.stop_reason,
            state.transitions,
            current_trace_id(),
        )
        result = _finalize(state)
        trace_id = current_trace_id()

    flush_observability()
    trace_url = dev_trace_url(trace_id)
    if trace_url:
        result["trace_url"] = trace_url
    return result
