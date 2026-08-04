"""Bounded client-tool selection (allowlist, heuristics, validation)."""

from __future__ import annotations

import json
import logging
import re
from typing import Iterable

logger = logging.getLogger(__name__)

TOOL_ALLOWLIST: tuple[str, ...] = (
    "get_client_profile",
    "get_account_summary",
    "get_account_restrictions",
    "get_recent_transactions",
    "get_open_service_requests",
    "get_interaction_history",
    "search_internal_policies",
)

CLIENT_TOOL_ALLOWLIST: tuple[str, ...] = (
    "get_client_profile",
    "get_account_summary",
    "get_account_restrictions",
    "get_recent_transactions",
    "get_open_service_requests",
    "get_interaction_history",
)

POLICY_TOOL_NAME = "search_internal_policies"

MAX_TOOLS_PER_RUN = 3
MAX_TOOLS_PER_ROUND = 1
FALLBACK_TOOLS: tuple[str, ...] = ("get_client_profile",)

_TOOL_SET = frozenset(TOOL_ALLOWLIST)
_CLIENT_TOOL_SET = frozenset(CLIENT_TOOL_ALLOWLIST)


def heuristic_tools(question: str) -> list[str]:
    """Cheap keyword boosts toward relevant tools."""
    q = (question or "").lower()
    picks: list[str] = []

    if any(
        token in q
        for token in (
            "pending",
            "transfer",
            "outbound",
            "transaction",
            "payment",
            "value date",
        )
    ):
        picks.append("get_recent_transactions")

    if any(
        token in q
        for token in (
            "portfolio",
            "holding",
            "holdings",
            "aum",
            "allocation",
            "performance",
            "market value",
            "custody",
            "asset mix",
            "what do they hold",
        )
    ):
        picks.append("get_account_summary")

    if any(
        token in q
        for token in (
            "restriction",
            "debit block",
            "freeze",
            "on hold",
            "blocked account",
        )
    ):
        picks.append("get_account_restrictions")

    if any(
        token in q
        for token in (
            "aml",
            "service request",
            "srq",
            "complaint",
            "open case",
            "ticket",
        )
    ):
        picks.append("get_open_service_requests")

    if any(
        token in q
        for token in (
            "interaction",
            "email",
            "call",
            "note",
            "awaiting reply",
            "thread",
            "complaint",
            "inbound",
            "nobody replied",
            "no reply",
        )
    ):
        picks.append("get_interaction_history")

    if any(
        token in q
        for token in (
            "kyc",
            "expired",
            "refresh due",
            "profile",
            "document expiry",
            "identity",
            "suitability",
            "questionnaire",
            "risk profile",
            "onboarding",
            "cross-border",
            "cross border",
            "preferred channel",
        )
    ):
        picks.append("get_client_profile")

    return picks


def parse_tool_names(raw: str) -> list[str]:
    """Extract tool names from LLM text (JSON list preferred)."""
    text = (raw or "").strip()
    if not text:
        return []

    # Prefer a JSON array somewhere in the response.
    match = re.search(r"\[[\s\S]*?\]", text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass

    # Fallback: comma / newline separated tokens.
    parts = re.split(r"[\n,]+", text)
    return [part.strip().strip('"').strip("'") for part in parts if part.strip()]


def normalize_selected_tools(
    candidates: Iterable[str],
    *,
    max_tools: int = MAX_TOOLS_PER_RUN,
    ensure_profile_if_any: bool = True,
    fallback_if_empty: bool = True,
    exclude: Iterable[str] = (),
) -> list[str]:
    """
    Keep allowlisted names only, stable order, hard cap.

    If any non-profile tool is chosen, include ``get_client_profile`` when room allows.
    Names in ``exclude`` (already called this run) are dropped.
    """
    excluded = frozenset(exclude)
    seen: set[str] = set()
    ordered: list[str] = []
    for name in candidates:
        if name not in _CLIENT_TOOL_SET or name in seen or name in excluded:
            continue
        seen.add(name)
        ordered.append(name)

    if (
        ensure_profile_if_any
        and ordered
        and "get_client_profile" not in seen
        and "get_client_profile" not in excluded
    ):
        ordered.insert(0, "get_client_profile")

    # Stable allowlist order for inspectability (client tools only).
    ordered = [name for name in CLIENT_TOOL_ALLOWLIST if name in set(ordered)]

    if not ordered and fallback_if_empty:
        ordered = [name for name in FALLBACK_TOOLS if name not in excluded]

    return ordered[:max_tools]


def merge_tool_choices(
    llm_names: Iterable[str],
    heuristic_names: Iterable[str],
    *,
    max_tools: int = MAX_TOOLS_PER_RUN,
    ensure_profile_if_any: bool = True,
    fallback_if_empty: bool = False,
    exclude: Iterable[str] = (),
) -> list[str]:
    """Union LLM + heuristic picks, then normalize."""
    combined = list(llm_names) + list(heuristic_names)
    selected = normalize_selected_tools(
        combined,
        max_tools=max_tools,
        ensure_profile_if_any=ensure_profile_if_any,
        fallback_if_empty=fallback_if_empty,
        exclude=exclude,
    )
    logger.info(
        "Tool selection merged: llm=%s heuristic=%s exclude=%s selected=%s",
        list(llm_names),
        list(heuristic_names),
        list(exclude),
        selected,
    )
    return selected
