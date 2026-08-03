"""Read-only tool: load recent interactions for a Helvetia client."""

from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.actor_read import actor_can_access_client, get_employee_by_code
from app.services.client_read import get_client_by_ref, list_client_interactions
from app.tools.base import ToolError, ToolResult, run_with_timeout

TOOL_NAME = "get_interaction_history"

_SALIENT_STATUSES = frozenset(
    {
        "open",
        "awaiting_reply",
        "pending",
        "in_progress",
    }
)


class GetInteractionHistoryInput(BaseModel):
    """Typed input for ``get_interaction_history``."""

    client_ref: str = Field(..., min_length=1, description="Client UUID or client_code")
    actor_employee_code: str | None = Field(
        default=None,
        description="Optional demo actor employee_code for book-scope checks",
    )
    limit: int = Field(default=8, ge=1, le=50)


def _is_salient(row) -> bool:
    status = (row.status or "").lower()
    direction = (row.direction or "").lower()
    return status in _SALIENT_STATUSES or direction == "inbound"


def _slim_row(row) -> dict:
    return {
        "channel": row.channel,
        "direction": row.direction,
        "subject": row.subject,
        "summary": row.summary,
        "status": row.status,
        "occurred_at": row.occurred_at.isoformat() if row.occurred_at else None,
        "employee_code": row.employee_code,
        "related_request_code": row.related_request_code,
    }


def _slim_interactions(interactions, *, limit: int) -> dict:
    rows = [_slim_row(item) for item in interactions[:limit]]
    salient = [
        row for row, item in zip(rows, interactions[:limit]) if _is_salient(item)
    ]
    return {
        "interaction_count": len(interactions),
        "returned_count": len(rows),
        "salient_count": len(salient),
        "interactions": rows,
        "salient_interactions": salient,
    }


def _execute(session: Session, payload: GetInteractionHistoryInput) -> ToolResult:
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

    interactions = list_client_interactions(session, client)
    return ToolResult(
        tool=TOOL_NAME,
        ok=True,
        data=_slim_interactions(interactions, limit=payload.limit),
    )


def get_interaction_history(
    session: Session,
    payload: GetInteractionHistoryInput | dict,
    *,
    timeout_seconds: float = 5.0,
) -> ToolResult:
    """
    Load recent client interactions with optional Act-as scope.

    Empty books return ``ok=True`` with empty lists — never invent a thread.
    """
    if not isinstance(payload, GetInteractionHistoryInput):
        payload = GetInteractionHistoryInput.model_validate(payload)

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
