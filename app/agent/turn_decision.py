"""Structured ReAct turn decisions (call_tool | search_policies | finish)."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Literal

from app.agent.tool_selection import TOOL_ALLOWLIST

logger = logging.getLogger(__name__)

TurnAction = Literal["call_tool", "search_policies", "finish"]

_TOOL_SET = frozenset(TOOL_ALLOWLIST)

_REASON_CODES = frozenset(
    {
        "verify_assertion",
        "need_profile",
        "need_transactions",
        "need_restrictions",
        "need_account_summary",
        "need_service_requests",
        "need_interactions",
        "need_policy",
        "enough_evidence",
        "no_client_tools_needed",
        "lookups_exhausted",
        "max_tool_rounds",
        "llm_fallback_finish",
        "llm_fallback_tool",
        "llm_fallback_policy",
        "no_client_ref",
        "invalid_decision",
    }
)

_MIN_POLICY_QUERY_LEN = 3


@dataclass(frozen=True)
class TurnDecision:
    """One bounded agent turn: call a tool, search policies, or finish the loop."""

    action: TurnAction
    tool: str | None = None
    policy_query: str | None = None
    reason_code: str = "enough_evidence"

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "tool": self.tool,
            "policy_query": self.policy_query,
            "reason_code": self.reason_code,
        }


def _normalize_reason(raw: Any) -> str:
    text = str(raw or "").strip().lower().replace(" ", "_")
    if text in _REASON_CODES:
        return text
    if text:
        cleaned = re.sub(r"[^a-z0-9_]+", "_", text)[:64].strip("_")
        return cleaned or "invalid_decision"
    return "invalid_decision"


def _extract_json_object(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def parse_turn_decision(
    raw: str,
    *,
    already_called: list[str] | None = None,
    already_searched: list[str] | None = None,
) -> TurnDecision | None:
    """
    Parse LLM text into a TurnDecision.

    Returns ``None`` when the payload is missing or violates the turn contract.
    """
    payload = _extract_json_object(raw)
    if payload is None:
        return None

    action = str(payload.get("action") or "").strip().lower()
    reason_code = _normalize_reason(payload.get("reason_code"))
    called = set(already_called or [])
    searched = {q.strip().lower() for q in (already_searched or []) if q and q.strip()}

    if action == "finish":
        return TurnDecision(action="finish", tool=None, policy_query=None, reason_code=reason_code)

    if action == "search_policies":
        policy_query = str(payload.get("policy_query") or "").strip()
        if len(policy_query) < _MIN_POLICY_QUERY_LEN:
            return None
        if policy_query.lower() in searched:
            return None
        return TurnDecision(
            action="search_policies",
            tool=None,
            policy_query=policy_query,
            reason_code=reason_code,
        )

    if action != "call_tool":
        return None

    tool = payload.get("tool")
    if isinstance(tool, list):
        return None
    tool_name = str(tool or "").strip()
    if tool_name not in _TOOL_SET or tool_name in called:
        return None

    return TurnDecision(
        action="call_tool",
        tool=tool_name,
        policy_query=None,
        reason_code=reason_code,
    )


def decision_from_fallback_tool(
    tool_name: str,
    *,
    reason_code: str = "llm_fallback_tool",
) -> TurnDecision:
    """Build a call_tool decision for deterministic round-0 fallback."""
    if tool_name not in _TOOL_SET:
        return TurnDecision(
            action="finish",
            tool=None,
            policy_query=None,
            reason_code="llm_fallback_finish",
        )
    return TurnDecision(
        action="call_tool",
        tool=tool_name,
        policy_query=None,
        reason_code=reason_code,
    )


def search_policies_decision(
    policy_query: str,
    *,
    reason_code: str = "need_policy",
) -> TurnDecision:
    """Build a search_policies decision for deterministic fallback."""
    query = policy_query.strip()
    if len(query) < _MIN_POLICY_QUERY_LEN:
        return finish_decision("invalid_decision")
    return TurnDecision(
        action="search_policies",
        tool=None,
        policy_query=query,
        reason_code=reason_code,
    )


def finish_decision(reason_code: str) -> TurnDecision:
    return TurnDecision(
        action="finish",
        tool=None,
        policy_query=None,
        reason_code=_normalize_reason(reason_code),
    )
