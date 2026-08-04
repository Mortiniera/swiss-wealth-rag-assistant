"""Deterministic next-step routing for the bounded agent workflow."""

from __future__ import annotations

from app.agent.state import AgentState

# Terminal sentinel, runner stops when routing returns this.
END = "__end__"

STEP_CLASSIFY = "classify"
STEP_SELECT_TOOLS = "select_tools"
STEP_RUN_TOOLS = "run_tools"
STEP_REWRITE = "rewrite"
STEP_GENERATE = "generate"
STEP_RESPOND_META = "respond_meta"
STEP_RESPOND_OOS = "respond_oos"


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
            return STEP_SELECT_TOOLS
        return STEP_REWRITE

    if state.step == STEP_SELECT_TOOLS:
        # Empty selection ends the tool loop (enough evidence / no tools needed).
        if not state.selected_tools:
            return STEP_REWRITE
        return STEP_RUN_TOOLS

    if state.step == STEP_RUN_TOOLS:
        # Continue the ReAct loop until the round cap; selector may still stop earlier.
        if state.tool_round >= state.max_tool_rounds:
            return STEP_REWRITE
        return STEP_SELECT_TOOLS

    if state.step == STEP_REWRITE:
        return STEP_GENERATE

    if state.step in (STEP_GENERATE, STEP_RESPOND_META, STEP_RESPOND_OOS):
        return END

    return END
