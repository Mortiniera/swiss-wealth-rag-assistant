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
    Empty transaction books are stated explicitly so the model does not invent them.
    """
    profile: dict[str, Any] | None = None
    restrictions_payload: dict[str, Any] | None = None
    transactions_payload: dict[str, Any] | None = None
    failed_txn_lookup = False

    for result in tool_results:
        tool = result.get("tool")
        if tool == "get_recent_transactions" and not result.get("ok"):
            failed_txn_lookup = True
            continue
        if not result.get("ok"):
            continue
        data = result.get("data") or {}
        if tool == "get_client_profile":
            profile = data
        elif tool == "get_account_restrictions":
            restrictions_payload = data
        elif tool == "get_recent_transactions":
            transactions_payload = data

    if (
        profile is None
        and restrictions_payload is None
        and transactions_payload is None
        and not failed_txn_lookup
    ):
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

    if failed_txn_lookup:
        lines.append(
            "Transaction lookup unavailable for this run — do not claim that "
            "transactions exist or that none exist; say the lookup failed."
        )
    elif transactions_payload is not None:
        total = int(transactions_payload.get("transaction_count") or 0)
        pending = transactions_payload.get("pending_or_unusual") or []
        if total == 0:
            lines.append(
                "Recent transactions: none on file for this client. "
                "Do not invent a pending outbound transfer. If the user asks why a "
                "transfer is pending, say you do not see a pending outbound in the book."
            )
        elif not pending:
            newest = (transactions_payload.get("transactions") or [{}])[0]
            lines.append(
                "Recent transactions on file ({total}), but none are pending, in review, "
                "or flagged unusual (newest: {code} status={status}). "
                "Do not invent a stuck transfer.".format(
                    total=total,
                    code=newest.get("transaction_code") or "n/a",
                    status=_humanize_status(newest.get("status")),
                )
            )
        else:
            for txn in pending:
                delay = txn.get("delay_reason_code")
                delay_bit = (
                    f", delay reason {_humanize_status(delay)}" if delay else ""
                )
                primary.append(
                    "Pending or unusual transaction {code} on {account}: "
                    "{txn_type} {amount} {currency}, status {status}{delay} — "
                    "cite this concrete movement; do not invent other transfers.".format(
                        code=txn.get("transaction_code") or "?",
                        account=txn.get("account_code") or "?",
                        txn_type=_humanize_status(txn.get("txn_type")),
                        amount=txn.get("amount") or "?",
                        currency=txn.get("currency") or "",
                        status=_humanize_status(txn.get("status")),
                        delay=delay_bit,
                    )
                )

    if primary:
        numbered = "\n".join(f"{i}. {text}" for i, text in enumerate(primary, start=1))
        insert_at = 1 if profile is not None else 0
        lines.insert(
            insert_at,
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

        elif tool == "get_recent_transactions":
            pending = data.get("pending_or_unusual") or []
            if int(data.get("transaction_count") or 0) == 0:
                items.append(
                    {
                        "label": "Transactions",
                        "value": "none on file",
                        "source": "recent_transactions",
                    }
                )
            elif not pending:
                items.append(
                    {
                        "label": "Pending txn",
                        "value": "none",
                        "source": "recent_transactions",
                    }
                )
            else:
                for txn in pending[:3]:
                    amount = txn.get("amount") or "?"
                    currency = txn.get("currency") or ""
                    status = _humanize_status(txn.get("status"))
                    code = txn.get("transaction_code") or "?"
                    items.append(
                        {
                            "label": "Pending txn",
                            "value": f"{code} · {amount} {currency} · {status}".strip(),
                            "source": "recent_transactions",
                        }
                    )
                    delay = txn.get("delay_reason_code")
                    if delay:
                        items.append(
                            {
                                "label": "Delay",
                                "value": _humanize_status(delay),
                                "source": "recent_transactions",
                            }
                        )

    return items
