"""Read-only tool: load recent transactions for a Helvetia client."""

from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.actor_read import actor_can_access_client, get_employee_by_code
from app.services.client_read import get_client_by_ref, list_client_transactions
from app.tools.base import ToolError, ToolResult, run_with_timeout

TOOL_NAME = "get_recent_transactions"

_PENDING_STATUSES = frozenset(
    {
        "pending",
        "pending_review",
        "in_review",
        "held",
        "blocked",
    }
)


class GetRecentTransactionsInput(BaseModel):
    """Typed input for ``get_recent_transactions``."""

    client_ref: str = Field(..., min_length=1, description="Client UUID or client_code")
    actor_employee_code: str | None = Field(
        default=None,
        description="Optional demo actor employee_code for book-scope checks",
    )
    limit: int = Field(default=10, ge=1, le=50)


def _is_salient(txn) -> bool:
    status = (txn.status or "").lower()
    return status in _PENDING_STATUSES or bool(txn.is_unusual) or bool(txn.delay_reason_code)


def _slim_row(txn) -> dict:
    return {
        "transaction_code": txn.transaction_code,
        "account_code": txn.account_code,
        "txn_type": txn.txn_type,
        "amount": str(txn.amount),
        "currency": txn.currency,
        "status": txn.status,
        "booked_at": txn.booked_at.isoformat() if txn.booked_at else None,
        "value_date": txn.value_date.isoformat() if txn.value_date else None,
        "counterparty_name": txn.counterparty_name,
        "delay_reason_code": txn.delay_reason_code,
        "is_unusual": bool(txn.is_unusual),
    }


def _slim_transactions(transactions, *, limit: int) -> dict:
    """Cap rows and flag which are pending/unusual for the agent."""
    rows = [_slim_row(txn) for txn in transactions[:limit]]
    salient = [row for row, txn in zip(rows, transactions[:limit]) if _is_salient(txn)]
    return {
        "transaction_count": len(transactions),
        "returned_count": len(rows),
        "pending_or_unusual_count": len(salient),
        "transactions": rows,
        "pending_or_unusual": salient,
    }


def _execute(session: Session, payload: GetRecentTransactionsInput) -> ToolResult:
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

    transactions = list_client_transactions(session, client)
    return ToolResult(
        tool=TOOL_NAME,
        ok=True,
        data=_slim_transactions(transactions, limit=payload.limit),
    )


def get_recent_transactions(
    session: Session,
    payload: GetRecentTransactionsInput | dict,
    *,
    timeout_seconds: float = 5.0,
) -> ToolResult:
    """
    Load recent client transactions with optional Act-as scope enforcement.

    Empty books return ``ok=True`` with empty lists — never invent rows.
    """
    if not isinstance(payload, GetRecentTransactionsInput):
        payload = GetRecentTransactionsInput.model_validate(payload)

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
