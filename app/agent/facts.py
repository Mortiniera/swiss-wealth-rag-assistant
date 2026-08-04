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
    account_summary_payload: dict[str, Any] | None = None
    restrictions_payload: dict[str, Any] | None = None
    transactions_payload: dict[str, Any] | None = None
    service_requests_payload: dict[str, Any] | None = None
    interactions_payload: dict[str, Any] | None = None
    failed_account_summary_lookup = False
    failed_txn_lookup = False
    failed_sr_lookup = False
    failed_interaction_lookup = False

    for result in tool_results:
        tool = result.get("tool")
        if tool == "get_account_summary" and not result.get("ok"):
            failed_account_summary_lookup = True
            continue
        if tool == "get_recent_transactions" and not result.get("ok"):
            failed_txn_lookup = True
            continue
        if tool == "get_open_service_requests" and not result.get("ok"):
            failed_sr_lookup = True
            continue
        if tool == "get_interaction_history" and not result.get("ok"):
            failed_interaction_lookup = True
            continue
        if not result.get("ok"):
            continue
        data = result.get("data") or {}
        if tool == "get_client_profile":
            profile = data
        elif tool == "get_account_summary":
            account_summary_payload = data
        elif tool == "get_account_restrictions":
            restrictions_payload = data
        elif tool == "get_recent_transactions":
            transactions_payload = data
        elif tool == "get_open_service_requests":
            service_requests_payload = data
        elif tool == "get_interaction_history":
            interactions_payload = data

    if (
        profile is None
        and account_summary_payload is None
        and restrictions_payload is None
        and transactions_payload is None
        and service_requests_payload is None
        and interactions_payload is None
        and not failed_account_summary_lookup
        and not failed_txn_lookup
        and not failed_sr_lookup
        and not failed_interaction_lookup
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

        suit_raw = (profile.get("suitability_status") or "").lower()
        suit = _humanize_status(profile.get("suitability_status"))
        risk = profile.get("suitability_risk_profile") or "n/a"
        if suit_raw in {"missing", "outdated", "incomplete"}:
            primary.append(
                f"Suitability {suit} (risk profile {risk}) — cite this gap; "
                "do not claim the questionnaire is complete."
            )
        elif suit_raw:
            lines.append(f"Suitability on file: {suit} (risk profile {risk}).")
        elif "suitability_status" in profile:
            lines.append(
                "Suitability profile: none on file. "
                "Do not invent a completed questionnaire."
            )

        channel = profile.get("preferred_channel")
        cross_border = profile.get("cross_border_ok")
        language = profile.get("preferred_language")
        if channel or cross_border is not None or language:
            cross_bit = (
                "unspecified"
                if cross_border is None
                else ("yes" if cross_border else "no")
            )
            lines.append(
                f"Communication prefs: channel={channel or 'n/a'}, "
                f"language={language or 'n/a'}, cross_border_ok={cross_bit}."
            )
            if cross_border is False:
                primary.append(
                    "Cross-border communication is not consented "
                    f"(residency {profile.get('residency_country') or 'n/a'}) — "
                    "do not recommend outbound contact that ignores this flag."
                )

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

    if failed_account_summary_lookup:
        lines.append(
            "Account summary lookup unavailable for this run — do not claim that "
            "holdings exist or that none exist; say the lookup failed."
        )
    elif account_summary_payload is not None:
        holding_count = int(account_summary_payload.get("holding_count") or 0)
        accounts = account_summary_payload.get("accounts") or []
        for account in accounts:
            code = account.get("account_code") or "?"
            status = _humanize_status(account.get("status"))
            if (account.get("status") or "").lower() == "restricted":
                primary.append(
                    f"Account {code} is marked restricted on file — verify holds, "
                    "debit blocks, or compliance flags on this account."
                )
            else:
                lines.append(f"Account {code}: status {status}.")
        if holding_count == 0:
            lines.append(
                "Account holdings: none on file for this client. "
                "Do not invent portfolio positions or market values."
            )
        else:
            for account in accounts:
                holdings = account.get("holdings") or []
                if not holdings:
                    continue
                total = account.get("holdings_market_value_total") or "?"
                currency = (
                    account.get("base_currency")
                    or account.get("currency")
                    or ""
                )
                as_of = account.get("portfolio_as_of") or "n/a"
                lines.append(
                    "Portfolio snapshot on {account} (as of {as_of}): "
                    "{count} holding(s), total market value {total} {currency}.".format(
                        account=account.get("account_code") or "?",
                        as_of=as_of,
                        count=len(holdings),
                        total=total,
                        currency=currency,
                    )
                )
                for holding in holdings[:8]:
                    lines.append(
                        "- {symbol} ({name}): qty {qty}, "
                        "market value {value} {ccy}".format(
                            symbol=holding.get("asset_symbol") or "?",
                            name=holding.get("asset_name") or "n/a",
                            qty=holding.get("quantity") or "?",
                            value=holding.get("market_value") or "?",
                            ccy=holding.get("currency") or "",
                        )
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
        restricted_accounts = [
            account.get("account_code")
            for account in (account_summary_payload or {}).get("accounts") or []
            if (account.get("status") or "").lower() == "restricted"
            and account.get("account_code")
        ]
        if restricted_accounts:
            for code in restricted_accounts:
                primary.append(
                    f"Account {code} is marked restricted on file — verify holds, "
                    "debit blocks, or compliance flags on this account."
                )
        else:
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
            primary.append(
                "Recent transactions: none on file for this client. "
                "If the user asks why a transfer is pending, lead with that absence — "
                "do not invent a pending outbound, and do not use KYC/suitability/"
                "restriction gaps as a cause for a transfer that is not in the book."
            )
        elif not pending:
            newest = (transactions_payload.get("transactions") or [{}])[0]
            primary.append(
                "No pending, in-review, or unusual outbound transfer is on file "
                "({total} recent movement(s); newest {code} status={status}). "
                "If the user asks why a transfer is pending, lead with that absence — "
                "do not invent a stuck transfer, and do not invent a cause "
                "(KYC, suitability, restriction, SLA) for one that is not evidenced.".format(
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

    if failed_sr_lookup:
        lines.append(
            "Service-request lookup unavailable for this run — do not claim that "
            "open cases exist or that none exist; say the lookup failed."
        )
    elif service_requests_payload is not None:
        open_requests = service_requests_payload.get("open_requests") or []
        if not open_requests:
            lines.append(
                "Open service requests: none on file. "
                "Do not invent an open AML or ops case."
            )
        else:
            for req in open_requests:
                primary.append(
                    "Open service request {code}: type {rtype}, status {status}, "
                    "priority {priority}, subject '{subject}' — cite this case; "
                    "do not invent other open requests.".format(
                        code=req.get("request_code") or "?",
                        rtype=_humanize_status(req.get("request_type")),
                        status=_humanize_status(req.get("status")),
                        priority=_humanize_status(req.get("priority")),
                        subject=(req.get("subject") or "n/a")[:120],
                    )
                )

    if failed_interaction_lookup:
        lines.append(
            "Interaction lookup unavailable for this run — do not claim that "
            "notes or emails exist or that none exist; say the lookup failed."
        )
    elif interactions_payload is not None:
        total = int(interactions_payload.get("interaction_count") or 0)
        salient = interactions_payload.get("salient_interactions") or []
        if total == 0:
            lines.append(
                "Interactions: none on file for this client. "
                "Do not invent a complaint thread, inbound email, or call note."
            )
        elif not salient:
            newest = (interactions_payload.get("interactions") or [{}])[0]
            lines.append(
                "Interactions on file ({total}), but none are inbound or awaiting "
                "reply (newest: {channel} {direction}, status={status}). "
                "Do not invent an unanswered client message.".format(
                    total=total,
                    channel=_humanize_status(newest.get("channel")),
                    direction=_humanize_status(newest.get("direction")),
                    status=_humanize_status(newest.get("status")),
                )
            )
        else:
            for item in salient:
                linked = item.get("related_request_code")
                linked_bit = f", linked to {linked}" if linked else ""
                primary.append(
                    "Interaction ({channel} {direction}): status {status}, "
                    "subject '{subject}'{linked} — cite this touchpoint; "
                    "do not invent other notes.".format(
                        channel=_humanize_status(item.get("channel")),
                        direction=_humanize_status(item.get("direction")),
                        status=_humanize_status(item.get("status")),
                        subject=(item.get("subject") or item.get("summary") or "n/a")[
                            :120
                        ],
                        linked=linked_bit,
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
            if data.get("suitability_status"):
                items.append(
                    {
                        "label": "Suitability",
                        "value": _humanize_status(data["suitability_status"]),
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
            if data.get("preferred_channel"):
                items.append(
                    {
                        "label": "Channel",
                        "value": _humanize_status(data["preferred_channel"]),
                        "source": "client_profile",
                    }
                )
            if data.get("cross_border_ok") is False:
                items.append(
                    {
                        "label": "Cross-border",
                        "value": "not consented",
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

        elif tool == "get_account_summary":
            holding_count = int(data.get("holding_count") or 0)
            if holding_count == 0:
                items.append(
                    {
                        "label": "Holdings",
                        "value": "none on file",
                        "source": "account_summary",
                    }
                )
            else:
                accounts = data.get("accounts") or []
                for account in accounts:
                    holdings = account.get("holdings") or []
                    if not holdings:
                        continue
                    total = account.get("holdings_market_value_total") or "?"
                    currency = (
                        account.get("base_currency")
                        or account.get("currency")
                        or ""
                    )
                    code = account.get("account_code") or "?"
                    items.append(
                        {
                            "label": "Holdings",
                            "value": (
                                f"{code} · {len(holdings)} lines · "
                                f"{total} {currency}".strip()
                            ),
                            "source": "account_summary",
                        }
                    )
                    for holding in holdings[:3]:
                        symbol = holding.get("asset_symbol") or "?"
                        value = holding.get("market_value") or "?"
                        ccy = holding.get("currency") or ""
                        items.append(
                            {
                                "label": "Position",
                                "value": f"{symbol} · {value} {ccy}".strip(),
                                "source": "account_summary",
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

        elif tool == "get_open_service_requests":
            open_requests = data.get("open_requests") or []
            if not open_requests:
                items.append(
                    {
                        "label": "Open SR",
                        "value": "none",
                        "source": "open_service_requests",
                    }
                )
            else:
                for req in open_requests[:3]:
                    code = req.get("request_code") or "?"
                    rtype = _humanize_status(req.get("request_type"))
                    items.append(
                        {
                            "label": "Open SR",
                            "value": f"{code} · {rtype}",
                            "source": "open_service_requests",
                        }
                    )

        elif tool == "get_interaction_history":
            salient = data.get("salient_interactions") or []
            if int(data.get("interaction_count") or 0) == 0:
                items.append(
                    {
                        "label": "Interaction",
                        "value": "none on file",
                        "source": "interaction_history",
                    }
                )
            elif not salient:
                items.append(
                    {
                        "label": "Inbound",
                        "value": "none awaiting reply",
                        "source": "interaction_history",
                    }
                )
            else:
                for item in salient[:3]:
                    channel = _humanize_status(item.get("channel"))
                    direction = _humanize_status(item.get("direction"))
                    status = _humanize_status(item.get("status"))
                    items.append(
                        {
                            "label": "Interaction",
                            "value": f"{channel} · {direction} · {status}",
                            "source": "interaction_history",
                        }
                    )

    return items
