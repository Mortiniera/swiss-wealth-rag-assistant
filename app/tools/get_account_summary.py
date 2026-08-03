"""Read-only tool: load account / holdings snapshot for a Helvetia client."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.schemas.clients import AccountSummaryOut
from app.services.actor_read import actor_can_access_client, get_employee_by_code
from app.services.client_read import get_client_by_ref, list_client_account_summaries
from app.tools.base import ToolError, ToolResult, run_with_timeout

TOOL_NAME = "get_account_summary"


class GetAccountSummaryInput(BaseModel):
    """Typed input for ``get_account_summary``."""

    client_ref: str = Field(..., min_length=1, description="Client UUID or client_code")
    actor_employee_code: str | None = Field(
        default=None,
        description="Optional demo actor employee_code for book-scope checks",
    )


def _holding_row(holding) -> dict:
    return {
        "asset_symbol": holding.asset_symbol,
        "asset_name": holding.asset_name,
        "quantity": str(holding.quantity),
        "market_value": str(holding.market_value),
        "currency": holding.currency,
    }


def _account_row(account: AccountSummaryOut) -> dict:
    holdings = [_holding_row(h) for h in account.holdings]
    total = sum((h.market_value for h in account.holdings), Decimal("0"))
    return {
        "account_code": account.account_code,
        "account_type": account.account_type,
        "currency": account.currency,
        "status": account.status,
        "portfolio_name": account.portfolio_name,
        "portfolio_as_of": (
            account.portfolio_as_of.isoformat() if account.portfolio_as_of else None
        ),
        "base_currency": account.base_currency,
        "holdings_count": len(holdings),
        "holdings_market_value_total": str(total),
        "holdings": holdings,
    }


def _slim_summary(accounts: list[AccountSummaryOut]) -> dict:
    """Flatten accounts + holdings into a compact payload for the agent."""
    rows = [_account_row(account) for account in accounts]
    holding_count = sum(row["holdings_count"] for row in rows)
    return {
        "account_count": len(rows),
        "holding_count": holding_count,
        "accounts": rows,
    }


def _execute(session: Session, payload: GetAccountSummaryInput) -> ToolResult:
    client = get_client_by_ref(session, payload.client_ref)
    if client is None:
        return ToolResult(
            tool=TOOL_NAME,
            ok=False,
            error=ToolError(
                code="not_found",
                message=f"Client '{payload.client_ref}' was not found",
            ),
        )

    if payload.actor_employee_code:
        actor = get_employee_by_code(session, payload.actor_employee_code)
        if actor is None:
            return ToolResult(
                tool=TOOL_NAME,
                ok=False,
                error=ToolError(
                    code="forbidden",
                    message=f"Unknown demo actor '{payload.actor_employee_code}'",
                ),
            )
        if not actor_can_access_client(session, actor, client):
            return ToolResult(
                tool=TOOL_NAME,
                ok=False,
                error=ToolError(
                    code="forbidden",
                    message=(
                        f"Actor '{payload.actor_employee_code}' cannot access "
                        f"client '{payload.client_ref}'"
                    ),
                ),
            )

    accounts = list_client_account_summaries(session, client)
    return ToolResult(tool=TOOL_NAME, ok=True, data=_slim_summary(accounts))


def get_account_summary(
    session: Session,
    payload: GetAccountSummaryInput | dict,
    *,
    timeout_seconds: float = 5.0,
) -> ToolResult:
    """
    Load account / holdings snapshot with optional Act-as scope enforcement.

    Empty books return ``ok=True`` with empty lists — never invent holdings.
    """
    if not isinstance(payload, GetAccountSummaryInput):
        payload = GetAccountSummaryInput.model_validate(payload)

    try:
        return run_with_timeout(
            lambda: _execute(session, payload),
            timeout_seconds=timeout_seconds,
        )
    except TimeoutError as exc:
        return ToolResult(
            tool=TOOL_NAME,
            ok=False,
            error=ToolError(code="timeout", message=str(exc)),
        )
    except Exception as exc:  # noqa: BLE001 — tools must not crash the workflow
        return ToolResult(
            tool=TOOL_NAME,
            ok=False,
            error=ToolError(code="error", message=str(exc)),
        )
