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
    profile: dict[str, Any] | None = None
    restrictions_payload: dict[str, Any] | None = None

    for result in tool_results:
        if not result.get("ok"):
            continue
        tool = result.get("tool")
        data = result.get("data") or {}
        if tool == "get_client_profile":
            profile = data
        elif tool == "get_account_restrictions":
            restrictions_payload = data

    if profile is None and restrictions_payload is None:
        return None

    lines: list[str] = []
    primary: list[str] = []

    if profile is not None:
        name = profile.get("full_name") or "Unknown client"
        code = profile.get("client_code") or "?"
        lines.append(f"Client: {name} ({code})")

        kyc_raw = (profile.get("kyc_status") or "").lower()
        kyc = _humanize_status(profile.get("kyc_status"))
        doc_type = profile.get("kyc_document_type") or "n/a"
        expiry = profile.get("kyc_document_expiry") or "n/a"
        if kyc_raw in {"expired", "refresh_due"}:
            primary.append(
                f"KYC {kyc} ({doc_type}, expiry {expiry}) — matches an "
                "enhanced-review / pending-review trigger when identity documents "
                "are expired or KYC refresh is due."
            )
        elif kyc_raw:
            lines.append(f"KYC on file: {kyc} ({doc_type}, expiry {expiry}).")

        rm = (
            profile.get("primary_rm_name")
            or profile.get("primary_rm_code")
            or "unassigned"
        )
        lines.append(
            f"Also on file: status={profile.get('status') or '?'}, "
            f"segment={profile.get('segment') or '?'}, "
            f"residency={profile.get('residency_country') or '?'}, "
            f"primary RM={rm}"
        )

    restrictions = (restrictions_payload or {}).get("restrictions") or []
    if restrictions:
        for item in restrictions:
            rtype = _humanize_status(item.get("restriction_type"))
            account = item.get("account_code") or "?"
            reason = item.get("reason_code") or "n/a"
            primary.append(
                f"Active account restriction on {account}: {rtype} "
                f"(reason {reason}) — matches a pending-review trigger when an "
                "account has an active restriction such as debit block, freeze, "
                "or manual review."
            )
    elif restrictions_payload is not None:
        lines.append("Active account restrictions: none on file.")

    if primary:
        numbered = "\n".join(f"{i}. {text}" for i, text in enumerate(primary, start=1))
        lines.insert(
            1 if profile is not None else 0,
            "Primary signal(s) — lead with these; if several apply, say so clearly:\n"
            + numbered,
        )

    return "\n".join(lines) if lines else None


def evidence_from_tool_results(
    tool_results: list[dict[str, Any]],
) -> list[dict[str, str]]:
    """Map successful tool payloads to AskResponse evidence chips."""
    items: list[dict[str, str]] = []
    for result in tool_results:
        if not result.get("ok"):
            continue
        tool = result.get("tool")
        data = result.get("data") or {}

        if tool == "get_client_profile":
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

        elif tool == "get_account_restrictions":
            for restriction in data.get("restrictions") or []:
                rtype = _humanize_status(restriction.get("restriction_type"))
                account = restriction.get("account_code") or "?"
                items.append(
                    {
                        "label": "Restriction",
                        "value": f"{rtype} · {account}",
                        "source": "account_restrictions",
                    }
                )

    return items
