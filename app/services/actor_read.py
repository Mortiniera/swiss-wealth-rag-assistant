"""Resolve demo actors and role-based read scopes (no auth session)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.models.people import Client, ClientAssignment, Employee, Role
from app.schemas.actors import (
    ActorOut,
    ClientScope,
    PanelLayoutOut,
    WorkspaceContextOut,
)

_CLIENT_LOAD = (
    selectinload(Client.household),
    selectinload(Client.kyc_profile),
    selectinload(Client.suitability_profile),
    selectinload(Client.communication_preference),
    selectinload(Client.assignments).selectinload(ClientAssignment.employee),
)

# Soft panel preference by role — returned by API so the UI does not invent ACL.
_PANEL_LAYOUTS: dict[str, PanelLayoutOut] = {
    "relationship_manager": PanelLayoutOut(
        focus_hint="Relationship view — full client record for your assigned book.",
        primary=[
            "profile",
            "accounts",
            "transactions",
            "service_requests",
            "interactions",
        ],
        secondary=[],
    ),
    "client_service": PanelLayoutOut(
        focus_hint="Service preference — requests and interactions first.",
        primary=[
            "service_requests",
            "interactions",
            "transactions",
            "profile",
            "accounts",
        ],
        secondary=[],
    ),
    "compliance_viewer": PanelLayoutOut(
        focus_hint="Compliance preference — KYC, restrictions, and transfers first.",
        primary=["profile", "accounts", "transactions"],
        secondary=["service_requests", "interactions"],
    ),
}


def build_actor_out(employee: Employee) -> ActorOut:
    return ActorOut(
        employee_code=employee.employee_code,
        full_name=employee.full_name,
        email=employee.email,
        role_code=employee.role.code,
        role_name=employee.role.name,
    )


def list_actors(session: Session) -> list[Employee]:
    """Active employees with roles, ordered for the Act-as picker."""
    return list(
        session.scalars(
            select(Employee)
            .options(selectinload(Employee.role))
            .where(Employee.is_active.is_(True))
            .join(Role)
            .order_by(Role.code, Employee.employee_code)
        ).all()
    )


def get_employee_by_code(session: Session, employee_code: str) -> Employee | None:
    return session.scalar(
        select(Employee)
        .options(selectinload(Employee.role))
        .where(Employee.employee_code == employee_code)
    )


def client_scope_for_role(role_code: str) -> ClientScope:
    if role_code == "relationship_manager":
        return "assigned"
    return "all"


def panel_layout_for_role(role_code: str) -> PanelLayoutOut:
    return _PANEL_LAYOUTS.get(
        role_code,
        _PANEL_LAYOUTS["relationship_manager"],
    )


def build_workspace_context(employee: Employee) -> WorkspaceContextOut:
    role_code = employee.role.code
    return WorkspaceContextOut(
        actor=build_actor_out(employee),
        client_scope=client_scope_for_role(role_code),
        panel_layout=panel_layout_for_role(role_code),
    )


def list_clients_for_actor(
    session: Session,
    employee: Employee,
    *,
    scenarios_only: bool = False,
) -> list[Client]:
    """Clients visible to this demo actor (RM = assigned book; others = all)."""
    stmt = select(Client).options(*_CLIENT_LOAD).order_by(Client.client_code)
    if scenarios_only:
        stmt = stmt.where(Client.client_code.like("CLI-SCEN-%"))

    if client_scope_for_role(employee.role.code) == "assigned":
        stmt = (
            stmt.join(ClientAssignment, ClientAssignment.client_id == Client.id)
            .where(ClientAssignment.employee_id == employee.id)
            .distinct()
        )

    return list(session.scalars(stmt).all())


def actor_can_access_client(session: Session, employee: Employee, client: Client) -> bool:
    if client_scope_for_role(employee.role.code) == "all":
        return True
    return (
        session.scalar(
            select(ClientAssignment.id).where(
                ClientAssignment.client_id == client.id,
                ClientAssignment.employee_id == employee.id,
            )
        )
        is not None
    )
