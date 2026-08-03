"""Bounded client-tool selection (allowlist, heuristics, validation)."""

from __future__ import annotations

import json
import logging
import re
from typing import Iterable

logger = logging.getLogger(__name__)

TOOL_ALLOWLIST: tuple[str, ...] = (
    "get_client_profile",
    "get_account_restrictions",
    "get_recent_transactions",
    "get_open_service_requests",
    "get_interaction_history",
)

MAX_TOOLS_PER_RUN = 3
FALLBACK_TOOLS: tuple[str, ...] = ("get_client_profile",)

_TOOL_SET = frozenset(TOOL_ALLOWLIST)


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
            "restriction",
            "debit block",
            "freeze",
            "hold",
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
) -> list[str]:
    """
    Keep allowlisted names only, stable order, hard cap.

    If any non-profile tool is chosen, include ``get_client_profile`` when room allows.
    """
    seen: set[str] = set()
    ordered: list[str] = []
    for name in candidates:
        if name not in _TOOL_SET or name in seen:
            continue
        seen.add(name)
        ordered.append(name)

    if ensure_profile_if_any and ordered and "get_client_profile" not in seen:
        ordered.insert(0, "get_client_profile")

    # Stable allowlist order for inspectability.
    ordered = [name for name in TOOL_ALLOWLIST if name in set(ordered)]

    if not ordered and fallback_if_empty:
        ordered = list(FALLBACK_TOOLS)

    return ordered[:max_tools]


def merge_tool_choices(
    llm_names: Iterable[str],
    heuristic_names: Iterable[str],
    *,
    max_tools: int = MAX_TOOLS_PER_RUN,
    fallback_if_empty: bool = False,
) -> list[str]:
    """Union LLM + heuristic picks, then normalize."""
    combined = list(llm_names) + list(heuristic_names)
    selected = normalize_selected_tools(
        combined,
        max_tools=max_tools,
        fallback_if_empty=fallback_if_empty,
    )
    logger.info(
        "Tool selection merged: llm=%s heuristic=%s selected=%s",
        list(llm_names),
        list(heuristic_names),
        selected,
    )
    return selected
