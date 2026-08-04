"""Read-only queries backing the client verification API."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.database.models import (
    Account,
    Client,
    ClientAssignment,
    Interaction,
    Portfolio,
    Restriction,
    ServiceRequest,
    Transaction,
)
from app.schemas.clients import (
    AccountOut,
    AccountSummaryOut,
    ClientOut,
    CommunicationPreferenceOut,
    HoldingOut,
    InteractionOut,
    KYCProfileOut,
    PrimaryAssignmentOut,
    RestrictionOut,
    ServiceRequestOut,
    SuitabilityProfileOut,
    TransactionOut,
)

PENDING_TXN_STATUSES = ("pending", "pending_review")


_CLIENT_LOAD_OPTIONS = (
    selectinload(Client.household),
    selectinload(Client.kyc_profile),
    selectinload(Client.suitability_profile),
    selectinload(Client.communication_preference),
    selectinload(Client.assignments).selectinload(ClientAssignment.employee),
)


def get_client_by_ref(session: Session, client_ref: str) -> Client | None:
    """Load a client by UUID string or stable ``client_code``."""
    try:
        client_id = uuid.UUID(client_ref)
    except ValueError:
        client_id = None

    stmt = select(Client).options(*_CLIENT_LOAD_OPTIONS)
    if client_id is not None:
        stmt = stmt.where(Client.id == client_id)
    else:
        stmt = stmt.where(Client.client_code == client_ref)

    return session.scalar(stmt)


def list_clients(session: Session, *, scenarios_only: bool = False) -> list[Client]:
    """List clients, optionally limited to ``CLI-SCEN-*`` demo scenarios."""
    stmt = select(Client).options(*_CLIENT_LOAD_OPTIONS).order_by(Client.client_code)
    if scenarios_only:
        stmt = stmt.where(Client.client_code.like("CLI-SCEN-%"))
    return list(session.scalars(stmt).all())


def _kyc_open_items(client: Client) -> list[str]:
    """KYC-only open-item signals (no extra queries)."""
    if client.kyc_profile is None:
        return []
    status = (client.kyc_profile.status or "").lower()
    if status == "expired":
        return ["KYC expired"]
    if status in ("pending", "in_review"):
        return ["KYC pending"]
    return []


def open_item_signals_by_client_id(
    session: Session, clients: list[Client]
) -> dict[uuid.UUID, list[str]]:
    """
    Batch-load directory open-item signals for the given clients.

    Priority order per client:
    KYC expired → KYC pending → Restriction → Pending transfer →
    SLA breach → Open SR.
    """
    if not clients:
        return {}

    client_ids = [client.id for client in clients]
    signals: dict[uuid.UUID, list[str]] = {
        client.id: _kyc_open_items(client) for client in clients
    }

    restricted_ids = set(
        session.scalars(
            select(Account.client_id)
            .where(
                Account.client_id.in_(client_ids),
                Account.status == "restricted",
            )
            .distinct()
        ).all()
    )

    restriction_rows = session.execute(
        select(Restriction.client_id, Account.client_id)
        .outerjoin(Account, Restriction.account_id == Account.id)
        .where(
            Restriction.status == "active",
            or_(
                Restriction.client_id.in_(client_ids),
                Account.client_id.in_(client_ids),
            ),
        )
    ).all()
    for restriction_client_id, account_client_id in restriction_rows:
        if restriction_client_id in signals:
            restricted_ids.add(restriction_client_id)
        if account_client_id in signals:
            restricted_ids.add(account_client_id)

    for client_id in restricted_ids:
        signals[client_id].append("Restriction")

    pending_ids = set(
        session.scalars(
            select(Account.client_id)
            .join(Transaction, Transaction.account_id == Account.id)
            .where(
                Account.client_id.in_(client_ids),
                Transaction.status.in_(PENDING_TXN_STATUSES),
            )
            .distinct()
        ).all()
    )
    for client_id in pending_ids:
        signals[client_id].append("Pending transfer")

    open_srs = session.execute(
        select(ServiceRequest.client_id, ServiceRequest.sla_due_at).where(
            ServiceRequest.client_id.in_(client_ids),
            ServiceRequest.status == "open",
        )
    ).all()
    now = datetime.now(timezone.utc)
    open_sr_ids: set[uuid.UUID] = set()
    sla_breach_ids: set[uuid.UUID] = set()
    for sr_client_id, sla_due_at in open_srs:
        open_sr_ids.add(sr_client_id)
        if sla_due_at is None:
            continue
        due = sla_due_at if sla_due_at.tzinfo else sla_due_at.replace(tzinfo=timezone.utc)
        if due < now:
            sla_breach_ids.add(sr_client_id)

    for client_id in sla_breach_ids:
        signals[client_id].append("SLA breach")
    for client_id in open_sr_ids - sla_breach_ids:
        signals[client_id].append("Open SR")

    return signals


def build_client_out(
    client: Client, *, open_items: list[str] | None = None
) -> ClientOut:
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
        open_items=(
            list(open_items) if open_items is not None else _kyc_open_items(client)
        ),
    )


def build_client_outs(session: Session, clients: list[Client]) -> list[ClientOut]:
    """Map clients to API responses with batch-loaded open-item signals."""
    signals = open_item_signals_by_client_id(session, clients)
    return [
        build_client_out(client, open_items=signals.get(client.id, []))
        for client in clients
    ]


def _holdings_from_portfolio(portfolio: Portfolio | None) -> list[HoldingOut]:
    if portfolio is None:
        return []
    return [
        HoldingOut(
            asset_symbol=row.asset_symbol,
            asset_name=row.asset_name,
            quantity=row.quantity,
            market_value=row.market_value,
            currency=row.currency,
        )
        for row in sorted(portfolio.holdings, key=lambda h: h.asset_symbol)
    ]


def list_client_accounts(session: Session, client: Client) -> list[AccountOut]:
    """Return accounts with restrictions and portfolio holdings."""
    accounts = session.scalars(
        select(Account)
        .where(Account.client_id == client.id)
        .options(
            selectinload(Account.restrictions),
            selectinload(Account.portfolio).selectinload(Portfolio.holdings),
        )
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
                RestrictionOut.model_validate(r)
                for r in account.restrictions
                if (r.status or "").lower() == "active"
            ],
            portfolio_name=account.portfolio.name if account.portfolio else None,
            portfolio_as_of=account.portfolio.as_of if account.portfolio else None,
            base_currency=(
                account.portfolio.base_currency if account.portfolio else None
            ),
            holdings=_holdings_from_portfolio(account.portfolio),
        )
        for account in accounts
    ]


def list_client_account_summaries(
    session: Session, client: Client
) -> list[AccountSummaryOut]:
    """Return accounts with portfolio holdings for account-summary tools."""
    accounts = session.scalars(
        select(Account)
        .where(Account.client_id == client.id)
        .options(selectinload(Account.portfolio).selectinload(Portfolio.holdings))
        .order_by(Account.account_code)
    ).all()

    summaries: list[AccountSummaryOut] = []
    for account in accounts:
        portfolio = account.portfolio
        summaries.append(
            AccountSummaryOut(
                account_code=account.account_code,
                account_type=account.account_type,
                currency=account.currency,
                status=account.status,
                portfolio_name=portfolio.name if portfolio else None,
                portfolio_as_of=portfolio.as_of if portfolio else None,
                base_currency=portfolio.base_currency if portfolio else None,
                holdings=_holdings_from_portfolio(portfolio),
            )
        )
    return summaries


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
