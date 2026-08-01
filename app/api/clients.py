"""Read-only client verification routes for Helvetia structured data."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.clients import (
    AccountOut,
    ClientOut,
    InteractionOut,
    ServiceRequestOut,
    TransactionOut,
)
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


def _require_client(session: Session, client_ref: str):
    """Resolve ``client_ref`` or raise HTTP 404."""
    client = get_client_by_ref(session, client_ref)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("", response_model=list[ClientOut])
def get_clients(
    scenarios_only: bool = Query(
        False,
        description="When true, return only CLI-SCEN-* demo scenario clients.",
    ),
    session: Session = Depends(get_db),
) -> list[ClientOut]:
    """Return clients for the operations directory."""
    clients = list_clients(session, scenarios_only=scenarios_only)
    return [build_client_out(client) for client in clients]


@router.get("/{client_ref}", response_model=ClientOut)
def get_client(client_ref: str, session: Session = Depends(get_db)) -> ClientOut:
    """Return client profile, compliance records, and primary RM assignment.

    ``client_ref`` accepts a UUID or stable ``client_code`` (e.g. ``CLI-SCEN-01``).
    """
    client = _require_client(session, client_ref)
    return build_client_out(client)


@router.get("/{client_ref}/accounts", response_model=list[AccountOut])
def get_client_accounts(
    client_ref: str, session: Session = Depends(get_db)
) -> list[AccountOut]:
    """Return accounts for the client, including account-level restrictions."""
    client = _require_client(session, client_ref)
    return list_client_accounts(session, client)


@router.get("/{client_ref}/transactions", response_model=list[TransactionOut])
def get_client_transactions(
    client_ref: str, session: Session = Depends(get_db)
) -> list[TransactionOut]:
    """Return transactions across all client accounts, newest first."""
    client = _require_client(session, client_ref)
    return list_client_transactions(session, client)


@router.get("/{client_ref}/interactions", response_model=list[InteractionOut])
def get_client_interactions(
    client_ref: str, session: Session = Depends(get_db)
) -> list[InteractionOut]:
    """Return interaction history for the client, newest first."""
    client = _require_client(session, client_ref)
    return list_client_interactions(session, client)


@router.get("/{client_ref}/service-requests", response_model=list[ServiceRequestOut])
def get_client_service_requests(
    client_ref: str, session: Session = Depends(get_db)
) -> list[ServiceRequestOut]:
    """Return service requests for the client, newest opened first."""
    client = _require_client(session, client_ref)
    return list_client_service_requests(session, client)
