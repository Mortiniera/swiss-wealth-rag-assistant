"""Read-only queries backing the client verification API."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database.models import (
    Account,
    Client,
    ClientAssignment,
    Interaction,
    Restriction,
    ServiceRequest,
    Transaction,
)
from app.schemas.clients import (
    AccountOut,
    ClientOut,
    CommunicationPreferenceOut,
    InteractionOut,
    KYCProfileOut,
    PrimaryAssignmentOut,
    RestrictionOut,
    ServiceRequestOut,
    SuitabilityProfileOut,
    TransactionOut,
)


def get_client_by_ref(session: Session, client_ref: str) -> Client | None:
    """Load a client by UUID string or stable ``client_code``."""
    try:
        client_id = uuid.UUID(client_ref)
    except ValueError:
        client_id = None

    stmt = select(Client).options(
        selectinload(Client.household),
        selectinload(Client.kyc_profile),
        selectinload(Client.suitability_profile),
        selectinload(Client.communication_preference),
        selectinload(Client.assignments).selectinload(ClientAssignment.employee),
    )
    if client_id is not None:
        stmt = stmt.where(Client.id == client_id)
    else:
        stmt = stmt.where(Client.client_code == client_ref)

    return session.scalar(stmt)


def build_client_out(client: Client) -> ClientOut:
    """Map a loaded ORM client graph to the API response schema."""
    primary = next((a for a in client.assignments if a.is_primary), None)
    primary_out = None
    if primary and primary.employee:
        primary_out = PrimaryAssignmentOut(
            employee_code=primary.employee.employee_code,
            full_name=primary.employee.full_name,
            email=primary.employee.email,
        )

    return ClientOut(
        id=client.id,
        client_code=client.client_code,
        full_name=client.full_name,
        email=client.email,
        residency_country=client.residency_country,
        status=client.status,
        segment=client.segment,
        household_code=client.household.household_code if client.household else None,
        created_at=client.created_at,
        kyc_profile=(
            KYCProfileOut.model_validate(client.kyc_profile)
            if client.kyc_profile
            else None
        ),
        suitability_profile=(
            SuitabilityProfileOut.model_validate(client.suitability_profile)
            if client.suitability_profile
            else None
        ),
        communication_preference=(
            CommunicationPreferenceOut.model_validate(client.communication_preference)
            if client.communication_preference
            else None
        ),
        primary_assignment=primary_out,
    )


def list_client_accounts(session: Session, client: Client) -> list[AccountOut]:
    """Return accounts for the client with account-level restrictions."""
    accounts = session.scalars(
        select(Account)
        .where(Account.client_id == client.id)
        .options(selectinload(Account.restrictions))
        .order_by(Account.account_code)
    ).all()

    return [
        AccountOut(
            id=account.id,
            account_code=account.account_code,
            account_type=account.account_type,
            currency=account.currency,
            status=account.status,
            iban_synthetic=account.iban_synthetic,
            opened_at=account.opened_at,
            restrictions=[
                RestrictionOut.model_validate(r) for r in account.restrictions
            ],
        )
        for account in accounts
    ]


def list_client_transactions(session: Session, client: Client) -> list[TransactionOut]:
    """Return transactions across all client accounts, newest first."""
    rows = session.execute(
        select(Transaction, Account.account_code)
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.client_id == client.id)
        .order_by(Transaction.created_at.desc())
    ).all()

    return [
        TransactionOut(
            id=txn.id,
            transaction_code=txn.transaction_code,
            account_code=account_code,
            txn_type=txn.txn_type,
            amount=txn.amount,
            currency=txn.currency,
            status=txn.status,
            booked_at=txn.booked_at,
            value_date=txn.value_date,
            counterparty_name=txn.counterparty_name,
            description=txn.description,
            delay_reason_code=txn.delay_reason_code,
            is_unusual=txn.is_unusual,
            created_at=txn.created_at,
        )
        for txn, account_code in rows
    ]


def list_client_interactions(session: Session, client: Client) -> list[InteractionOut]:
    """Return client interactions, newest first."""
    interactions = session.scalars(
        select(Interaction)
        .where(Interaction.client_id == client.id)
        .options(
            selectinload(Interaction.related_service_request),
            selectinload(Interaction.employee),
        )
        .order_by(Interaction.occurred_at.desc())
    ).all()

    return [
        InteractionOut(
            id=row.id,
            channel=row.channel,
            direction=row.direction,
            subject=row.subject,
            summary=row.summary,
            occurred_at=row.occurred_at,
            status=row.status,
            employee_code=row.employee.employee_code if row.employee else None,
            related_request_code=(
                row.related_service_request.request_code
                if row.related_service_request
                else None
            ),
        )
        for row in interactions
    ]


def list_client_service_requests(
    session: Session, client: Client
) -> list[ServiceRequestOut]:
    """Return client service requests, newest opened first."""
    requests = session.scalars(
        select(ServiceRequest)
        .where(ServiceRequest.client_id == client.id)
        .options(selectinload(ServiceRequest.assigned_employee))
        .order_by(ServiceRequest.opened_at.desc())
    ).all()

    return [
        ServiceRequestOut(
            id=row.id,
            request_code=row.request_code,
            request_type=row.request_type,
            status=row.status,
            priority=row.priority,
            subject=row.subject,
            opened_at=row.opened_at,
            sla_due_at=row.sla_due_at,
            resolved_at=row.resolved_at,
            assigned_employee_code=(
                row.assigned_employee.employee_code if row.assigned_employee else None
            ),
        )
        for row in requests
    ]
