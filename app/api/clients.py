"""Read-only client verification routes for Helvetia structured data."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_optional_actor
from app.database.models.people import Employee
from app.database.session import get_db
from app.schemas.clients import (
    AccountOut,
    ClientOut,
    InteractionOut,
    ServiceRequestOut,
    TransactionOut,
)
from app.services.actor_read import actor_can_access_client, list_clients_for_actor
from app.services.client_read import (
    build_client_out,
    get_client_by_ref,
    list_client_accounts,
    list_client_interactions,
    list_client_service_requests,
    list_client_transactions,
    list_clients,
)

router = APIRouter(prefix="/clients", tags=["clients"])


def _require_client(
    session: Session,
    client_ref: str,
    actor: Employee | None,
):
    """Resolve ``client_ref`` and enforce demo-actor scope when provided."""
    client = get_client_by_ref(session, client_ref)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    if actor is not None and not actor_can_access_client(session, actor, client):
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("", response_model=list[ClientOut])
def get_clients(
    scenarios_only: bool = Query(
        False,
        description="When true, return only CLI-SCEN-* demo scenario clients.",
    ),
    session: Session = Depends(get_db),
    actor: Employee | None = Depends(get_optional_actor),
) -> list[ClientOut]:
    """Return clients for the operations directory.

    With ``X-Helvetia-Actor``, relationship managers only see assigned clients.
    """
    if actor is not None:
        clients = list_clients_for_actor(
            session, actor, scenarios_only=scenarios_only
        )
    else:
        clients = list_clients(session, scenarios_only=scenarios_only)
    return [build_client_out(client) for client in clients]


@router.get("/{client_ref}", response_model=ClientOut)
def get_client(
    client_ref: str,
    session: Session = Depends(get_db),
    actor: Employee | None = Depends(get_optional_actor),
) -> ClientOut:
    """Return client profile, compliance records, and primary RM assignment.

    ``client_ref`` accepts a UUID or stable ``client_code`` (e.g. ``CLI-SCEN-01``).
    """
    client = _require_client(session, client_ref, actor)
    return build_client_out(client)


@router.get("/{client_ref}/accounts", response_model=list[AccountOut])
def get_client_accounts(
    client_ref: str,
    session: Session = Depends(get_db),
    actor: Employee | None = Depends(get_optional_actor),
) -> list[AccountOut]:
    """Return accounts for the client, including account-level restrictions."""
    client = _require_client(session, client_ref, actor)
    return list_client_accounts(session, client)


@router.get("/{client_ref}/transactions", response_model=list[TransactionOut])
def get_client_transactions(
    client_ref: str,
    session: Session = Depends(get_db),
    actor: Employee | None = Depends(get_optional_actor),
) -> list[TransactionOut]:
    """Return transactions across all client accounts, newest first."""
    client = _require_client(session, client_ref, actor)
    return list_client_transactions(session, client)


@router.get("/{client_ref}/interactions", response_model=list[InteractionOut])
def get_client_interactions(
    client_ref: str,
    session: Session = Depends(get_db),
    actor: Employee | None = Depends(get_optional_actor),
) -> list[InteractionOut]:
    """Return interaction history for the client, newest first."""
    client = _require_client(session, client_ref, actor)
    return list_client_interactions(session, client)


@router.get("/{client_ref}/service-requests", response_model=list[ServiceRequestOut])
def get_client_service_requests(
    client_ref: str,
    session: Session = Depends(get_db),
    actor: Employee | None = Depends(get_optional_actor),
) -> list[ServiceRequestOut]:
    """Return service requests for the client, newest opened first."""
    client = _require_client(session, client_ref, actor)
    return list_client_service_requests(session, client)
