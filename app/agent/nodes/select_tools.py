"""Select which read-only client tools to run for this question."""

from __future__ import annotations

import logging

from llama_index.core import Settings as LlamaSettings

from app.agent.state import AgentState
from app.agent.tool_selection import (
    TOOL_ALLOWLIST,
    heuristic_tools,
    merge_tool_choices,
    parse_tool_names,
)
from app.rag.common import configure_llm
from app.rag.generator import _format_history

logger = logging.getLogger(__name__)


def _build_selection_prompt(state: AgentState) -> str:
    catalog = "\n".join(f"- {name}" for name in TOOL_ALLOWLIST)
    return f"""You choose read-only Helvetia banking tools for an internal ops assistant.
Pick only tools needed to answer the latest question about client {state.client_ref}.
Return a JSON array of tool names. Use an empty array [] if no structured client
lookup is needed (policy-only question). Never invent tool names.

Available tools:
{catalog}

Guidance:
- Pending / delayed / outbound transfer → get_recent_transactions (and usually profile)
- Portfolio / holdings / AUM / allocation → get_account_summary
- Account block / freeze / restriction → get_account_restrictions
- Open AML / complaint / service request → get_open_service_requests
- Complaint thread / email / call notes / awaiting reply → get_interaction_history
- KYC / identity / document expiry → get_client_profile
- Prefer at most 3 tools.

Conversation history:
{_format_history(state.history)}

Latest message: {state.question}

JSON array:"""


def run(state: AgentState) -> None:
    """Populate ``state.selected_tools`` from LLM + heuristics (bounded allowlist)."""
    if not state.client_ref:
        state.selected_tools = []
        return

    heuristic = heuristic_tools(state.question)
    llm_names: list[str] = []
    llm_failed = False

    try:
        configure_llm()
        response = LlamaSettings.llm.complete(_build_selection_prompt(state))
        llm_names = parse_tool_names(response.text)
    except Exception:  # noqa: BLE001 — selection must not crash the workflow
        llm_failed = True
        logger.exception("Tool selection LLM failed; using heuristics/fallback")

    state.selected_tools = merge_tool_choices(
        llm_names,
        heuristic,
        fallback_if_empty=llm_failed,
    )
    logger.info(
        "Selected tools for client_ref=%s: %s (llm_failed=%s)",
        state.client_ref,
        state.selected_tools,
        llm_failed,
    )
