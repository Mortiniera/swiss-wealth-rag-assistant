"""Demo actor / workspace-context schemas (not login — soft identity for v0.5)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

PanelId = Literal[
    "profile",
    "accounts",
    "transactions",
    "service_requests",
    "interactions",
]

ClientScope = Literal["assigned", "all"]


class ActorOut(BaseModel):
    """One seed employee available as a demo operator identity."""

    employee_code: str
    full_name: str
    email: str
    role_code: str
    role_name: str


class PanelLayoutOut(BaseModel):
    """How client detail panels are ordered for this role (presentation + soft hide)."""

    focus_hint: str
    primary: list[PanelId]
    secondary: list[PanelId] = Field(default_factory=list)


class WorkspaceContextOut(BaseModel):
    """Backend-driven view for the selected demo actor."""

    actor: ActorOut
    client_scope: ClientScope
    panel_layout: PanelLayoutOut
    note: str = (
        "Demo identity only — not authentication. "
        "API scopes lists using this actor; full RBAC lands in a later release."
    )
