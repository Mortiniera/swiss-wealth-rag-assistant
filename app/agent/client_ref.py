"""Helpers to resolve client scope from the user question."""

from __future__ import annotations

import re

# Matches dock prefix and free-form mentions: CLI-SCEN-01, CLI-000001, etc.
_CLIENT_CODE_RE = re.compile(r"\b(CLI-[A-Z0-9-]+)\b", re.IGNORECASE)
_UUID_RE = re.compile(
    r"\b([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\b",
    re.IGNORECASE,
)


def extract_client_ref(question: str) -> str | None:
    """Return the first client_code or UUID found in ``question``, if any."""
    code_match = _CLIENT_CODE_RE.search(question or "")
    if code_match:
        return code_match.group(1).upper()
    uuid_match = _UUID_RE.search(question or "")
    if uuid_match:
        return uuid_match.group(1).lower()
    return None
