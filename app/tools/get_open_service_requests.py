"""Read-only tool: load open service requests for a Helvetia client."""

from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.actor_read import actor_can_access_client, get_employee_by_code
from app.services.client_read import get_client_by_ref, list_client_service_requests
from app.tools.base import ToolError, ToolResult, run_with_timeout

TOOL_NAME = "get_open_service_requests"

_OPEN_STATUSES = frozenset(
    {
        "open",
        "in_progress",
        "pending",
        "assigned",
        "escalated",
    }
)


class GetOpenServiceRequestsInput(BaseModel):
    """Typed input for ``get_open_service_requests``."""

    client_ref: str = Field(..., min_length=1, description="Client UUID or client_code")
    actor_employee_code: str | None = Field(
        default=None,
        description="Optional demo actor employee_code for book-scope checks",
    )


def _slim_row(request) -> dict:
    return {
        "request_code": request.request_code,
        "request_type": request.request_type,
        "status": request.status,
        "priority": request.priority,
        "subject": request.subject,
        "opened_at": request.opened_at.isoformat() if request.opened_at else None,
        "sla_due_at": request.sla_due_at.isoformat() if request.sla_due_at else None,
        "assigned_employee_code": request.assigned_employee_code,
    }


def _slim_requests(requests) -> dict:
    open_rows = [
        _slim_row(req)
        for req in requests
        if (req.status or "").lower() in _OPEN_STATUSES
    ]
    return {
        "request_count": len(requests),
        "open_count": len(open_rows),
        "open_requests": open_rows,
    }


def _execute(session: Session, payload: GetOpenServiceRequestsInput) -> ToolResult:
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

    requests = list_client_service_requests(session, client)
    return ToolResult(tool=TOOL_NAME, ok=True, data=_slim_requests(requests))


def get_open_service_requests(
    session: Session,
    payload: GetOpenServiceRequestsInput | dict,
    *,
    timeout_seconds: float = 5.0,
) -> ToolResult:
    """
    Load open/in-progress service requests with optional Act-as scope.

    Empty open books return ``ok=True`` with empty lists — never invent cases.
    """
    if not isinstance(payload, GetOpenServiceRequestsInput):
        payload = GetOpenServiceRequestsInput.model_validate(payload)

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
