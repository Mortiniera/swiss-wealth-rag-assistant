"""Run the selected read-only client tools in stable order."""

from __future__ import annotations

import logging
from types import ModuleType

from app.agent.nodes import (
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
    "get_account_restrictions": fetch_restrictions,
    "get_recent_transactions": fetch_transactions,
    "get_open_service_requests": fetch_service_requests,
    "get_interaction_history": fetch_interactions,
}


def run(state: AgentState) -> None:
    """Execute each selected tool once; skip unknown names."""
    if not state.client_ref:
        return

    for tool_name in state.selected_tools:
        module = _TOOL_MODULES.get(tool_name)
        if module is None:
            logger.warning("Skipping unknown selected tool %r", tool_name)
            continue
        module.run(state)

    logger.info(
        "Ran selected tools: %s (results=%d)",
        state.selected_tools,
        len(state.tool_results),
    )
