"""Select the next read-only client tool for this ReAct round."""

from __future__ import annotations

import logging
from typing import Any

from llama_index.core import Settings as LlamaSettings

from app.agent.state import AgentState
from app.agent.tool_selection import (
    MAX_TOOLS_PER_ROUND,
    TOOL_ALLOWLIST,
    heuristic_tools,
    merge_tool_choices,
    parse_tool_names,
)
from app.rag.common import configure_llm
from app.rag.generator import _format_history

logger = logging.getLogger(__name__)


def _observation_digest(tool_results: list[dict[str, Any]]) -> str:
    """Compact observation lines for the next-round selector (not shown to operators)."""
    if not tool_results:
        return "(none yet)"

    lines: list[str] = []
    for result in tool_results:
        tool = result.get("tool") or "unknown"
        if not result.get("ok"):
            code = (result.get("error") or {}).get("code") or "error"
            lines.append(f"- {tool}: failed ({code})")
            continue
        data = result.get("data") or {}
        if tool == "get_client_profile":
            lines.append(
                f"- {tool}: kyc={data.get('kyc_status') or 'n/a'}, "
                f"suitability={data.get('suitability_status') or 'n/a'}, "
                f"segment={data.get('segment') or 'n/a'}"
            )
        elif tool == "get_account_summary":
            lines.append(
                f"- {tool}: accounts={data.get('account_count', 0)}, "
                f"holdings={data.get('holding_count', 0)}"
            )
        elif tool == "get_account_restrictions":
            lines.append(
                f"- {tool}: active_restrictions={data.get('restriction_count', 0)}"
            )
        elif tool == "get_recent_transactions":
            lines.append(
                f"- {tool}: txns={data.get('transaction_count', 0)}, "
                f"pending_or_unusual={data.get('pending_or_unusual_count', 0)}"
            )
        elif tool == "get_open_service_requests":
            open_count = data.get("open_count")
            if open_count is None:
                open_count = len(data.get("open_requests") or [])
            lines.append(f"- {tool}: open_requests={open_count}")
        elif tool == "get_interaction_history":
            lines.append(
                f"- {tool}: interactions={data.get('interaction_count', 0)}, "
                f"salient={len(data.get('salient_interactions') or [])}"
            )
        else:
            lines.append(f"- {tool}: ok")
    return "\n".join(lines)


def _build_selection_prompt(state: AgentState) -> str:
    catalog = "\n".join(f"- {name}" for name in TOOL_ALLOWLIST)
    already = ", ".join(state.tools_called) if state.tools_called else "(none)"
    remaining = [name for name in TOOL_ALLOWLIST if name not in set(state.tools_called)]
    remaining_catalog = "\n".join(f"- {name}" for name in remaining) or "(none left)"
    return f"""You choose the NEXT read-only Helvetia banking tool for an internal ops assistant.
This is tool round {state.tool_round + 1} of at most {state.max_tool_rounds} for client {state.client_ref}.
Return a JSON array with at most ONE tool name for this round.
Return [] if observations are enough to answer, or if no further structured lookup helps.
Never invent tool names. Do not repeat tools already called.

All tools:
{catalog}

Still available this run:
{remaining_catalog}

Already called: {already}

Observations so far:
{_observation_digest(state.tool_results)}

Guidance:
- Pending / delayed / outbound transfer → get_recent_transactions
- Portfolio / holdings / AUM / allocation → get_account_summary
- Account block / freeze / restriction → get_account_restrictions
- Open AML / complaint / service request → get_open_service_requests
- Complaint thread / email / call notes / awaiting reply → get_interaction_history
- KYC / identity / document expiry → get_client_profile
- Prefer exactly one tool per round.

Conversation history:
{_format_history(state.history)}

Latest message: {state.question}

JSON array:"""


def run(state: AgentState) -> None:
    """Pick the next allowlisted tool for this round (or stop with an empty list)."""
    if not state.client_ref:
        state.selected_tools = []
        state.stop_reason = state.stop_reason or "no_client_ref"
        return

    already = list(state.tools_called)
    heuristic = [name for name in heuristic_tools(state.question) if name not in already]
    llm_names: list[str] = []
    llm_failed = False

    try:
        configure_llm()
        response = LlamaSettings.llm.complete(_build_selection_prompt(state))
        llm_names = [
            name for name in parse_tool_names(response.text) if name not in already
        ]
    except Exception:  # noqa: BLE001 — selection must not crash the workflow
        llm_failed = True
        logger.exception("Tool selection LLM failed; using heuristics/fallback")

    # First round only: if the LLM fails, fall back to a single heuristic/profile tool.
    # Later rounds: empty means stop — do not invent follow-up calls.
    fallback = llm_failed and state.tool_round == 0
    state.selected_tools = merge_tool_choices(
        llm_names,
        heuristic,
        max_tools=MAX_TOOLS_PER_ROUND,
        ensure_profile_if_any=False,
        fallback_if_empty=fallback,
        exclude=already,
    )

    if not state.selected_tools:
        state.stop_reason = (
            "no_tools_needed" if state.tool_round == 0 else "enough_evidence"
        )
    else:
        # Clear prior stop if we continue (e.g. after a previous empty attempt).
        if state.stop_reason in {"no_tools_needed", "enough_evidence"}:
            state.stop_reason = None

    logger.info(
        "Selected tools for client_ref=%s round=%s: %s (llm_failed=%s stop_reason=%s)",
        state.client_ref,
        state.tool_round + 1,
        state.selected_tools,
        llm_failed,
        state.stop_reason,
    )
