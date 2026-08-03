"""Read-only tool: load account restrictions for a Helvetia client."""

from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.actor_read import actor_can_access_client, get_employee_by_code
from app.services.client_read import get_client_by_ref, list_client_accounts
from app.tools.base import ToolError, ToolResult, run_with_timeout

TOOL_NAME = "get_account_restrictions"


class GetAccountRestrictionsInput(BaseModel):
    """Typed input for ``get_account_restrictions``."""

    client_ref: str = Field(..., min_length=1, description="Client UUID or client_code")
    actor_employee_code: str | None = Field(
        default=None,
        description="Optional demo actor employee_code for book-scope checks",
    )


def _slim_restrictions(accounts) -> dict:
    """Flatten account restrictions into a compact payload for the agent."""
    active: list[dict] = []
    for account in accounts:
        for restriction in account.restrictions:
            status = (restriction.status or "").lower()
            if status != "active":
                continue
            active.append(
                {
                    "account_code": account.account_code,
                    "account_status": account.status,
                    "restriction_type": restriction.restriction_type,
                    "reason_code": restriction.reason_code,
                    "status": restriction.status,
                    "effective_from": (
                        restriction.effective_from.isoformat()
                        if restriction.effective_from
                        else None
                    ),
                }
            )
    return {
        "restriction_count": len(active),
        "restrictions": active,
    }


def _execute(session: Session, payload: GetAccountRestrictionsInput) -> ToolResult:
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

    accounts = list_client_accounts(session, client)
    return ToolResult(tool=TOOL_NAME, ok=True, data=_slim_restrictions(accounts))


def get_account_restrictions(
    session: Session,
    payload: GetAccountRestrictionsInput | dict,
    *,
    timeout_seconds: float = 5.0,
) -> ToolResult:
    """
    Load active account restrictions with optional Act-as scope enforcement.

    Never raises for business outcomes — returns ``ToolResult`` with structured errors.
    """
    if not isinstance(payload, GetAccountRestrictionsInput):
        payload = GetAccountRestrictionsInput.model_validate(payload)

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
