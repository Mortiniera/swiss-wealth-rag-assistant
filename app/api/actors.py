"""Demo actor catalog and workspace context (not authentication)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.actors import ActorOut, WorkspaceContextOut
from app.services.actor_read import (
    build_actor_out,
    build_workspace_context,
    get_employee_by_code,
    list_actors,
)

router = APIRouter(prefix="/actors", tags=["actors"])


@router.get("", response_model=list[ActorOut])
def get_actors(session: Session = Depends(get_db)) -> list[ActorOut]:
    """List seed employees for the Act-as demo identity picker."""
    return [build_actor_out(emp) for emp in list_actors(session)]


@router.get("/{employee_code}/workspace", response_model=WorkspaceContextOut)
def get_actor_workspace(
    employee_code: str, session: Session = Depends(get_db)
) -> WorkspaceContextOut:
    """Return scoped capabilities and panel layout for one demo actor."""
    employee = get_employee_by_code(session, employee_code)
    if employee is None:
        raise HTTPException(status_code=404, detail="Actor not found")
    return build_workspace_context(employee)
