"""Format tool results for generation prompts and API evidence chips."""

from __future__ import annotations

from typing import Any


def _humanize_status(value: str | None) -> str:
    if not value:
        return "unknown"
    return value.replace("_", " ").strip()


def format_structured_facts(tool_results: list[dict[str, Any]]) -> str | None:
    """
    Render ok tool payloads as an operator-salient facts block for the LLM.

    Failed tools are omitted here (still available on state for later UI/audit).
    """
    blocks: list[str] = []
    for result in tool_results:
        if not result.get("ok"):
            continue
        tool = result.get("tool")
        data = result.get("data") or {}
        if tool != "get_client_profile":
            continue

        name = data.get("full_name") or "Unknown client"
        code = data.get("client_code") or "?"
        kyc = _humanize_status(data.get("kyc_status"))
        doc_type = data.get("kyc_document_type") or "n/a"
        expiry = data.get("kyc_document_expiry") or "n/a"
        rm = (
            data.get("primary_rm_name")
            or data.get("primary_rm_code")
            or "unassigned"
        )

        kyc_raw = (data.get("kyc_status") or "").lower()
        if kyc_raw in {"expired", "refresh_due"}:
            signal = (
                f"Primary signal: KYC {kyc} ({doc_type}, expiry {expiry}) — "
                "this matches an enhanced-review / pending-review trigger when "
                "identity documents are expired or KYC refresh is due."
            )
        elif kyc_raw:
            signal = (
                f"KYC on file: {kyc} ({doc_type}, expiry {expiry}). "
                "Do not invent other blockers."
            )
        else:
            signal = "KYC profile not available in structured facts."

        blocks.append(
            "\n".join(
                [
                    f"Client: {name} ({code})",
                    signal,
                    (
                        f"Also on file: status={data.get('status') or '?'}, "
                        f"segment={data.get('segment') or '?'}, "
                        f"residency={data.get('residency_country') or '?'}, "
                        f"primary RM={rm}"
                    ),
                ]
            )
        )

    if not blocks:
        return None
    return "\n\n".join(blocks)


def evidence_from_tool_results(
    tool_results: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Map successful tool payloads to AskResponse evidence chips."""
    items: list[dict[str, str]] = []
    for result in tool_results:
        if not result.get("ok"):
            continue
        if result.get("tool") != "get_client_profile":
            continue
        data = result.get("data") or {}
        if data.get("kyc_status"):
            items.append(
                {
                    "label": "KYC",
                    "value": _humanize_status(data["kyc_status"]),
                    "source": "client_profile",
                }
            )
        if data.get("kyc_document_expiry"):
            items.append(
                {
                    "label": "Doc expiry",
                    "value": str(data["kyc_document_expiry"]),
                    "source": "client_profile",
                }
            )
        if data.get("segment"):
            items.append(
                {
                    "label": "Segment",
                    "value": str(data["segment"]),
                    "source": "client_profile",
                }
            )
        rm = data.get("primary_rm_name") or data.get("primary_rm_code")
        if rm:
            items.append(
                {
                    "label": "Primary RM",
                    "value": str(rm),
                    "source": "client_profile",
                }
            )
    return items
