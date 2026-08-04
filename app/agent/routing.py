"""Deterministic next-step routing for the bounded agent workflow."""

from __future__ import annotations

from app.agent.state import AgentState

# Terminal sentinel, runner stops when routing returns this.
END = "__end__"

STEP_CLASSIFY = "classify"
STEP_AGENT_TURN = "agent_turn"
STEP_RUN_TOOLS = "run_tools"
STEP_SEARCH_POLICIES = "search_policies"
STEP_REWRITE = "rewrite"
STEP_GENERATE = "generate"
STEP_RESPOND_META = "respond_meta"
STEP_RESPOND_OOS = "respond_oos"

# Back-compat alias for older tests/docs referring to select_tools.
STEP_SELECT_TOOLS = STEP_AGENT_TURN


def next_step(state: AgentState) -> str:
    """
    Return the next node name or ``END`` when the run should stop.

    Routing is pure: it only inspects state, never calls LLMs or I/O.
    """
    if state.status in ("completed", "failed"):
        return END

    if state.step is None:
        return STEP_CLASSIFY

    if state.step == STEP_CLASSIFY:
        if state.intent == "OUT_OF_SCOPE":
            return STEP_RESPOND_OOS
        if state.intent == "ASSISTANT_META":
            return STEP_RESPOND_META
        if state.client_ref:
            return STEP_AGENT_TURN
        return STEP_REWRITE

    if state.step == STEP_AGENT_TURN:
        decision = state.last_decision or {}
        action = decision.get("action")
        if action == "search_policies" and state.policy_query:
            return STEP_SEARCH_POLICIES
        if not state.selected_tools:
            return STEP_REWRITE
        return STEP_RUN_TOOLS

    if state.step == STEP_RUN_TOOLS:
        if state.tool_round >= state.max_tool_rounds:
            return STEP_REWRITE
        return STEP_AGENT_TURN

    if state.step == STEP_SEARCH_POLICIES:
        if state.tool_round >= state.max_tool_rounds:
            return STEP_REWRITE
        return STEP_AGENT_TURN

    if state.step == STEP_REWRITE:
        return STEP_GENERATE

    if state.step in (STEP_GENERATE, STEP_RESPOND_META, STEP_RESPOND_OOS):
        return END

    return END
