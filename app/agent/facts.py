"""Format successful tool results for the generation prompt."""

from __future__ import annotations

from typing import Any


def format_structured_facts(tool_results: list[dict[str, Any]]) -> str | None:
    """
    Render ok tool payloads as a short facts block for the LLM.

    Failed tools are omitted here (still available on state for later UI/audit).
    """
    lines: list[str] = []
    for result in tool_results:
        if not result.get("ok"):
            continue
        tool = result.get("tool")
        data = result.get("data") or {}
        if tool == "get_client_profile":
            lines.append(
                "- Client {code} ({name}): status={status}, segment={segment}, "
                "residency={residency}, KYC={kyc} (doc={doc_type}, expiry={expiry}), "
                "primary RM={rm}".format(
                    code=data.get("client_code") or "?",
                    name=data.get("full_name") or "?",
                    status=data.get("status") or "?",
                    segment=data.get("segment") or "?",
                    residency=data.get("residency_country") or "?",
                    kyc=data.get("kyc_status") or "unknown",
                    doc_type=data.get("kyc_document_type") or "n/a",
                    expiry=data.get("kyc_document_expiry") or "n/a",
                    rm=data.get("primary_rm_name")
                    or data.get("primary_rm_code")
                    or "unassigned",
                )
            )
    if not lines:
        return None
    return "\n".join(lines)
