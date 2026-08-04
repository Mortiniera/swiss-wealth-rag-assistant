"""Read-only tool: load a slim Helvetia client profile."""

from __future__ import annotations

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.actor_read import actor_can_access_client, get_employee_by_code
from app.services.client_read import build_client_out, get_client_by_ref
from app.tools.base import ToolError, ToolResult, run_with_timeout

TOOL_NAME = "get_client_profile"


class GetClientProfileInput(BaseModel):
    """Typed input for ``get_client_profile``."""

    client_ref: str = Field(..., min_length=1, description="Client UUID or client_code")
    actor_employee_code: str | None = Field(
        default=None,
        description="Optional demo actor employee_code for book-scope checks",
    )


def _slim_profile(client_out) -> dict:
    """Reduce ClientOut to facts useful for grounded answers."""
    kyc = client_out.kyc_profile
    suitability = client_out.suitability_profile
    prefs = client_out.communication_preference
    primary = client_out.primary_assignment
    return {
        "client_code": client_out.client_code,
        "full_name": client_out.full_name,
        "status": client_out.status,
        "segment": client_out.segment,
        "residency_country": client_out.residency_country,
        "kyc_status": kyc.status if kyc else None,
        "kyc_document_type": kyc.document_type if kyc else None,
        "kyc_document_expiry": (
            kyc.document_expiry.isoformat() if kyc and kyc.document_expiry else None
        ),
        "suitability_status": suitability.status if suitability else None,
        "suitability_risk_profile": (
            suitability.risk_profile if suitability else None
        ),
        "preferred_channel": prefs.preferred_channel if prefs else None,
        "cross_border_ok": prefs.cross_border_ok if prefs else None,
        "preferred_language": prefs.language if prefs else None,
        "primary_rm_code": primary.employee_code if primary else None,
        "primary_rm_name": primary.full_name if primary else None,
    }


def _execute(session: Session, payload: GetClientProfileInput) -> ToolResult:
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

    profile = build_client_out(client)
    return ToolResult(tool=TOOL_NAME, ok=True, data=_slim_profile(profile))


def get_client_profile(
    session: Session,
    payload: GetClientProfileInput | dict,
    *,
    timeout_seconds: float = 5.0,
) -> ToolResult:
    """
    Load a slim client profile with optional Act-as scope enforcement.

    Never raises for business outcomes — returns ``ToolResult`` with structured errors.
    Timeouts become ``ToolResult(ok=False, error.code='timeout')``.
    """
    if not isinstance(payload, GetClientProfileInput):
        payload = GetClientProfileInput.model_validate(payload)

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
