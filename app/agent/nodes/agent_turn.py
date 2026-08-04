"""Structured ReAct turn: verify assertions, gather evidence, search policies, finish."""

from __future__ import annotations

import logging
from typing import Any

from llama_index.core import Settings as LlamaSettings

from app.agent.state import AgentState
from app.agent.tool_selection import TOOL_ALLOWLIST, heuristic_tools
from app.agent.turn_decision import (
    TurnDecision,
    decision_from_fallback_tool,
    finish_decision,
    parse_turn_decision,
    search_policies_decision,
)
from app.rag.common import configure_llm
from app.rag.generator import _format_history

logger = logging.getLogger(__name__)


def _observation_digest(tool_results: list[dict[str, Any]], policy_queries: list[str]) -> str:
    """Compact observation lines for the next turn (not shown to operators)."""
    lines: list[str] = []
    if not tool_results and not policy_queries:
        return "(none yet)"

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
            accounts = data.get("accounts") or []
            restricted = [
                row.get("account_code")
                for row in accounts
                if (row.get("status") or "").lower() == "restricted"
                and row.get("account_code")
            ]
            restricted_bit = (
                f", restricted_accounts={','.join(restricted)}"
                if restricted
                else ", restricted_accounts=none"
            )
            lines.append(
                f"- {tool}: accounts={data.get('account_count', 0)}, "
                f"holdings={data.get('holding_count', 0)}{restricted_bit}"
            )
        elif tool == "get_account_restrictions":
            count = data.get("restriction_count", 0)
            codes = [
                row.get("account_code")
                for row in (data.get("restrictions") or [])
                if row.get("account_code")
            ]
            codes_bit = f" on {','.join(codes)}" if codes else ""
            lines.append(f"- {tool}: active_restrictions={count}{codes_bit}")
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

    for query in policy_queries:
        lines.append(f"- search_policies: ran query={query[:120]!r}")

    return "\n".join(lines) if lines else "(none yet)"


def _build_turn_prompt(state: AgentState) -> str:
    catalog = "\n".join(
        f"- {name}: {_tool_purpose(name)}" for name in TOOL_ALLOWLIST
    )
    already = ", ".join(state.tools_called) if state.tools_called else "(none)"
    remaining = [name for name in TOOL_ALLOWLIST if name not in set(state.tools_called)]
    remaining_catalog = "\n".join(f"- {name}" for name in remaining) or "(none left)"
    searched = ", ".join(state.policy_queries) if state.policy_queries else "(none)"
    return f"""You are the turn planner for Helvetia's internal ops assistant.
Decide the NEXT action for client {state.client_ref}.
This is loop round {state.tool_round + 1} of at most {state.max_tool_rounds}.

Return ONLY one JSON object with this exact shape:
{{"action":"call_tool"|"search_policies"|"finish","tool":"<name-or-null>","policy_query":"<text-or-null>","reason_code":"<code>"}}

Planning contract (general — apply to any question):
1. Parse the latest message: what is the user ASKING vs what do they ASSERT or ASSUME?
   Examples of assertions: "transfer is pending", "KYC expired", "account is blocked",
   "open complaint", "nobody replied".
2. VERIFY assertions first. If the user assumes a client fact, call the tool that directly
   checks that fact before finish. Do not finish while a central assertion is still unverified
   unless the verifying tool already ran (including empty/zero results) or failed.
3. After verification, call additional client tools only if needed to answer the question.
4. action=search_policies when procedure, SLA, thresholds, or policy rules are needed to
   answer. Set policy_query to a focused search string (not the full user message).
   Skip search_policies when verified facts alone answer the question — e.g. the user asked
   why something is pending but transactions show none pending.
5. action=finish when verified facts plus any policy context gathered are enough to answer
   honestly, including when an asserted fact is false or not on file.

Rules:
- action=call_tool: set tool to exactly ONE allowlisted name still available; policy_query null.
- action=search_policies: set policy_query (min 3 chars); tool null. Do not repeat a query
  already searched this run.
- action=finish: set tool and policy_query to null.
- Never invent tool names. Never return more than one action per turn.
- Empty-book observations (zero rows) still count as verification — do not retry the same tool.

Client tools (what each verifies):
{catalog}

Still available:
{remaining_catalog}

Already called: {already}
Policy searches already run: {searched}

Observations so far:
{_observation_digest(state.tool_results, state.policy_queries)}

Conversation history:
{_format_history(state.history)}

Latest message: {state.question}

JSON:"""


def _tool_purpose(name: str) -> str:
    purposes = {
        "get_client_profile": "identity, KYC status/expiry, suitability, segment, comms prefs",
        "get_account_summary": "accounts, holdings, AUM / portfolio on file",
        "get_account_restrictions": "active debit blocks, freezes, holds",
        "get_recent_transactions": "recent txns, pending/unusual outbound transfers",
        "get_open_service_requests": "open AML / complaint / ops service requests",
        "get_interaction_history": "emails, calls, notes, inbound threads",
    }
    return purposes.get(name, "client lookup")


def _apply_decision(state: AgentState, decision: TurnDecision) -> None:
    state.last_decision = decision.to_dict()
    state.selected_tools = []
    state.policy_query = None

    if decision.action == "call_tool" and decision.tool:
        state.selected_tools = [decision.tool]
        state.stop_reason = None
        return

    if decision.action == "search_policies" and decision.policy_query:
        state.policy_query = decision.policy_query
        state.stop_reason = None
        return

    state.stop_reason = decision.reason_code or "enough_evidence"
    state.round_trace.append(
        {
            "round": state.tool_round,
            "decision": decision.to_dict(),
            "selected": [],
        }
    )


def run(state: AgentState) -> None:
    """Decide call_tool, search_policies, or finish; record decision on state."""
    if not state.client_ref:
        decision = finish_decision("no_client_ref")
        _apply_decision(state, decision)
        return

    if state.tool_round >= state.max_tool_rounds:
        decision = finish_decision("max_tool_rounds")
        _apply_decision(state, decision)
        return

    already = list(state.tools_called)
    searched = list(state.policy_queries)
    decision: TurnDecision | None = None
    llm_failed = False

    try:
        configure_llm()
        response = LlamaSettings.llm.complete(_build_turn_prompt(state))
        decision = parse_turn_decision(
            response.text,
            already_called=already,
            already_searched=searched,
        )
    except Exception:  # noqa: BLE001 — turn planning must not crash the workflow
        llm_failed = True
        logger.exception("Agent turn LLM failed")

    if decision is None:
        if state.tool_round == 0:
            hints = [name for name in heuristic_tools(state.question) if name not in already]
            fallback_tool = hints[0] if hints else "get_client_profile"
            if fallback_tool in already:
                decision = finish_decision("llm_fallback_finish")
            else:
                decision = decision_from_fallback_tool(
                    fallback_tool,
                    reason_code="llm_fallback_tool",
                )
        elif not searched and _question_likely_needs_policy(state.question):
            decision = search_policies_decision(
                state.question[:200],
                reason_code="llm_fallback_policy",
            )
        else:
            decision = finish_decision("llm_fallback_finish")

    _apply_decision(state, decision)
    logger.info(
        "Agent turn client_ref=%s round=%s decision=%s llm_failed=%s",
        state.client_ref,
        state.tool_round + 1,
        decision.to_dict(),
        llm_failed,
    )


def _question_likely_needs_policy(question: str) -> bool:
    """Cheap fallback when the planner LLM fails on later rounds."""
    q = (question or "").lower()
    return any(
        token in q
        for token in (
            "policy",
            "procedure",
            "sla",
            "threshold",
            "rule",
            "allowed",
            "cadence",
            "refresh",
            "what should",
            "what do we",
        )
    )
