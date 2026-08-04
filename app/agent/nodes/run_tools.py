"""Run the selected read-only client tools for the current ReAct round."""

from __future__ import annotations

import logging
from types import ModuleType

from app.agent.nodes import (
    fetch_account_summary,
    fetch_interactions,
    fetch_profile,
    fetch_restrictions,
    fetch_service_requests,
    fetch_transactions,
)
from app.agent.state import AgentState

logger = logging.getLogger(__name__)

_TOOL_MODULES: dict[str, ModuleType] = {
    "get_client_profile": fetch_profile,
    "get_account_summary": fetch_account_summary,
    "get_account_restrictions": fetch_restrictions,
    "get_recent_transactions": fetch_transactions,
    "get_open_service_requests": fetch_service_requests,
    "get_interaction_history": fetch_interactions,
}


def run(state: AgentState) -> None:
    """Execute each selected tool once; record observation on state; advance round."""
    if not state.client_ref:
        return

    before = len(state.tool_results)
    ran: list[str] = []
    for tool_name in state.selected_tools:
        module = _TOOL_MODULES.get(tool_name)
        if module is None:
            logger.warning("Skipping unknown selected tool %r", tool_name)
            continue
        module.run(state)
        ran.append(tool_name)
        if tool_name not in state.tools_called:
            state.tools_called.append(tool_name)

    new_results = state.tool_results[before:]
    state.tool_round += 1
    state.round_trace.append(
        {
            "round": state.tool_round,
            "selected": list(ran),
            "tools": [row.get("tool") for row in new_results],
            "ok": [bool(row.get("ok")) for row in new_results],
        }
    )

    if state.tool_round >= state.max_tool_rounds:
        state.stop_reason = "max_tool_rounds"

    logger.info(
        "Ran tool round %s: selected=%s results=%d stop_reason=%s",
        state.tool_round,
        ran,
        len(new_results),
        state.stop_reason,
    )
