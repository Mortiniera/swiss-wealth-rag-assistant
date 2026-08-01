"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database.models.people import Employee
from app.database.session import get_db
from app.services.actor_read import get_employee_by_code

ACTOR_HEADER = "X-Helvetia-Actor"


def get_optional_actor(
    session: Session = Depends(get_db),
    x_helvetia_actor: Annotated[str | None, Header(alias=ACTOR_HEADER)] = None,
) -> Employee | None:
    """Resolve demo actor from ``X-Helvetia-Actor`` employee code, if present."""
    if not x_helvetia_actor:
        return None
    employee = get_employee_by_code(session, x_helvetia_actor.strip())
    if employee is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown demo actor '{x_helvetia_actor}'. Use GET /actors.",
        )
    return employee


def require_actor(
    actor: Employee | None = Depends(get_optional_actor),
) -> Employee:
    """Require a valid demo actor header."""
    if actor is None:
        raise HTTPException(
            status_code=400,
            detail=f"Missing {ACTOR_HEADER} header (employee_code from GET /actors).",
        )
    return actor
