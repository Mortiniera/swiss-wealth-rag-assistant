"""Shared builders for curated CLI-SCEN-* seed rows."""

from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.database.models import (
    Account,
    Client,
    ClientAssignment,
    CommunicationPreference,
    Employee,
    Holding,
    Interaction,
    KYCProfile,
    Portfolio,
    Restriction,
    ServiceRequest,
    SuitabilityProfile,
    Transaction,
)

DEFAULT_HOLDINGS: list[tuple[str, str, str, str]] = [
    ("NESN.SW", "Nestle SA", "120.5", "185000.00"),
    ("ROG.SW", "Roche Holding", "45.0", "142000.00"),
    ("CHF", "Swiss Franc Cash", "25000.0", "25000.00"),
]


def make_client(
    session: Session,
    n: int,
    *,
    full_name: str,
    status: str,
    residency_country: str,
    now: datetime,
    segment: str = "hnwi",
) -> Client:
    """Insert scenario client ``CLI-SCEN-NN`` and return it."""
    client = Client(
        id=uuid.uuid4(),
        client_code=f"CLI-SCEN-{n:02d}",
        full_name=full_name,
        email=f"scen.{n:02d}@clients.helvetia.example",
        residency_country=residency_country,
        status=status,
        household_id=None,
        segment=segment,
        created_at=now - timedelta(days=400 + n * 7),
    )
    session.add(client)
    session.flush()
    return client


def assign_rm(session: Session, client: Client, rm: Employee) -> None:
    """Insert a primary relationship-manager assignment for the client."""
    session.add(
        ClientAssignment(
            id=uuid.uuid4(),
            client_id=client.id,
            employee_id=rm.id,
            is_primary=True,
            assigned_at=client.created_at,
        )
    )


def make_account(
    session: Session,
    n: int,
    client: Client,
    *,
    status: str = "open",
    currency: str = "CHF",
    account_type: str = "custody",
) -> Account:
    """Insert scenario account ``ACC-SCEN-NN`` for the client."""
    account = Account(
        id=uuid.uuid4(),
        account_code=f"ACC-SCEN-{n:02d}",
        client_id=client.id,
        account_type=account_type,
        currency=currency,
        status=status,
        iban_synthetic=f"CH93SCEN{n:012d}",
        opened_at=client.created_at + timedelta(days=14),
    )
    session.add(account)
    session.flush()
    return account


def make_portfolio_with_holdings(
    session: Session,
    account: Account,
    *,
    now: datetime,
    holdings: list[tuple[str, str, str, str]] | None = None,
) -> Portfolio:
    """Insert one portfolio and holdings for the account.

    Each holding tuple is ``(symbol, name, quantity, market_value)``.
    """
    portfolio = Portfolio(
        id=uuid.uuid4(),
        account_id=account.id,
        name=f"Portfolio {account.account_code}",
        base_currency=account.currency,
        as_of=now - timedelta(days=1),
    )
    session.add(portfolio)
    session.flush()

    for symbol, name, qty, value in holdings or DEFAULT_HOLDINGS:
        session.add(
            Holding(
                id=uuid.uuid4(),
                portfolio_id=portfolio.id,
                asset_symbol=symbol,
                asset_name=name,
                quantity=Decimal(qty),
                market_value=Decimal(value),
                currency=account.currency,
            )
        )
    return portfolio


def make_kyc(
    session: Session,
    client: Client,
    *,
    status: str,
    document_expiry: date,
    now: datetime,
    notes: str,
) -> KYCProfile:
    """Insert a KYC profile for the client."""
    profile = KYCProfile(
        id=uuid.uuid4(),
        client_id=client.id,
        status=status,
        document_type="passport",
        document_expiry=document_expiry,
        last_reviewed_at=now - timedelta(days=60),
        notes=notes,
    )
    session.add(profile)
    return profile


def make_suitability(
    session: Session,
    client: Client,
    *,
    status: str,
    now: datetime,
    risk_profile: str | None = "balanced",
) -> SuitabilityProfile:
    """Insert a suitability profile for the client."""
    profile = SuitabilityProfile(
        id=uuid.uuid4(),
        client_id=client.id,
        status=status,
        risk_profile=None if status == "missing" else risk_profile,
        completed_at=None if status == "missing" else now - timedelta(days=120),
    )
    session.add(profile)
    return profile


def make_comms(
    session: Session,
    client: Client,
    *,
    preferred_channel: str = "email",
    cross_border_ok: bool = True,
    language: str = "en",
) -> CommunicationPreference:
    """Insert communication preferences for the client."""
    pref = CommunicationPreference(
        id=uuid.uuid4(),
        client_id=client.id,
        preferred_channel=preferred_channel,
        marketing_opt_in=False,
        cross_border_ok=cross_border_ok,
        language=language,
    )
    session.add(pref)
    return pref


def make_txn(
    session: Session,
    n: int,
    account: Account,
    *,
    status: str,
    amount: str,
    now: datetime,
    description: str,
    delay_reason_code: str | None = None,
    is_unusual: bool = False,
    txn_type: str = "transfer_out",
    booked_offset_days: int | None = 3,
) -> Transaction:
    """Insert scenario transaction ``TXN-SCEN-NN`` on the account."""
    booked_at = (
        None if status == "pending" else now - timedelta(days=booked_offset_days or 3)
    )
    txn = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        transaction_code=f"TXN-SCEN-{n:02d}",
        txn_type=txn_type,
        amount=Decimal(amount),
        currency=account.currency,
        status=status,
        booked_at=booked_at,
        value_date=booked_at,
        counterparty_name="Helvetia Demo Counterparty",
        description=description,
        delay_reason_code=delay_reason_code,
        is_unusual=is_unusual,
        created_at=now - timedelta(days=booked_offset_days or 3),
    )
    session.add(txn)
    return txn


def make_restriction(
    session: Session,
    n: int,
    *,
    client: Client,
    account: Account | None,
    restriction_type: str,
    reason_code: str,
    now: datetime,
    notes: str,
) -> Restriction:
    """Insert an active restriction; notes are prefixed ``[RST-SCEN-NN]``."""
    row = Restriction(
        id=uuid.uuid4(),
        client_id=client.id,
        account_id=account.id if account else None,
        restriction_type=restriction_type,
        reason_code=reason_code,
        status="active",
        effective_from=now - timedelta(days=10),
        effective_to=None,
        notes=f"[RST-SCEN-{n:02d}] {notes}",
    )
    session.add(row)
    return row


def make_service_request(
    session: Session,
    n: int,
    client: Client,
    *,
    request_type: str,
    subject: str,
    now: datetime,
    priority: str = "medium",
    status: str = "open",
    sla_due_at: datetime | None = None,
    assigned: Employee | None = None,
) -> ServiceRequest:
    """Insert scenario service request ``SRQ-SCEN-NN``."""
    sr = ServiceRequest(
        id=uuid.uuid4(),
        request_code=f"SRQ-SCEN-{n:02d}",
        client_id=client.id,
        request_type=request_type,
        status=status,
        priority=priority,
        subject=subject,
        opened_at=now - timedelta(days=12),
        sla_due_at=sla_due_at,
        resolved_at=None,
        assigned_employee_id=assigned.id if assigned else None,
    )
    session.add(sr)
    session.flush()
    return sr


def make_interaction(
    session: Session,
    client: Client,
    *,
    employee: Employee | None,
    channel: str,
    direction: str,
    subject: str,
    summary: str,
    now: datetime,
    status: str = "logged",
    related: ServiceRequest | None = None,
    days_ago: int = 5,
) -> Interaction:
    """Insert a client interaction, optionally linked to a service request."""
    row = Interaction(
        id=uuid.uuid4(),
        client_id=client.id,
        employee_id=employee.id if employee else None,
        channel=channel,
        direction=direction,
        subject=subject,
        summary=summary,
        occurred_at=now - timedelta(days=days_ago),
        related_service_request_id=related.id if related else None,
        status=status,
    )
    session.add(row)
    return row
