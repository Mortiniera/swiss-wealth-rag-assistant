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

# Per-scenario packs so curated books are visually distinct (not one cloned book).
# Each tuple is ``(symbol, name, quantity, market_value)``.
SCENARIO_HOLDINGS: dict[int, list[tuple[str, str, str, str]]] = {
    1: [  # Helena — classic CH book, larger AUM under KYC hold
        ("NESN.SW", "Nestle SA", "180.0", "276000.00"),
        ("ROG.SW", "Roche Holding", "55.0", "168000.00"),
        ("CHF", "Swiss Franc Cash", "42000.0", "42000.00"),
    ],
    2: [  # Marcus — equity + bond mix under compliance block
        ("NESN.SW", "Nestle SA", "90.0", "138000.00"),
        ("AGG", "iShares Core US Aggregate Bond", "600.0", "62000.00"),
        ("CHF", "Swiss Franc Cash", "18000.0", "18000.00"),
    ],
    3: [
        ("VWRL.L", "Vanguard FTSE All-World", "220.0", "248000.00"),
        ("CHF", "Swiss Franc Cash", "35000.0", "35000.00"),
    ],
    4: [
        ("ROG.SW", "Roche Holding", "70.0", "215000.00"),
        ("NESN.SW", "Nestle SA", "40.0", "61000.00"),
        ("CHF", "Swiss Franc Cash", "12000.0", "12000.00"),
    ],
    5: [  # Thin / placeholder book (story: limited holdings)
        ("CHF", "Swiss Franc Cash", "1000.0", "1000.00"),
    ],
    6: [  # Noah — EUR custody (account currency EUR)
        ("NESN.SW", "Nestle SA", "95.0", "145000.00"),
        ("VWRL.L", "Vanguard FTSE All-World", "110.0", "124000.00"),
        ("EUR", "Euro Cash", "28000.0", "28000.00"),
    ],
    7: [
        ("AGG", "iShares Core US Aggregate Bond", "900.0", "94000.00"),
        ("ROG.SW", "Roche Holding", "25.0", "76000.00"),
        ("CHF", "Swiss Franc Cash", "22000.0", "22000.00"),
    ],
    8: [  # Luca — US residency / cross-border
        ("AGG", "iShares Core US Aggregate Bond", "1200.0", "126000.00"),
        ("VWRL.L", "Vanguard FTSE All-World", "60.0", "68000.00"),
        ("USD", "US Dollar Cash", "15000.0", "15000.00"),
    ],
    9: [  # Sparse global ETF book
        ("VWRL.L", "Vanguard FTSE All-World", "80.0", "95000.00"),
        ("CHF", "Swiss Franc Cash", "500.0", "500.00"),
    ],
    10: [  # Portfolio performance enquiry — intentional Nestlé overweight
        ("NESN.SW", "Nestle SA", "200.0", "210000.00"),
        ("ROG.SW", "Roche Holding", "30.0", "88000.00"),
        ("AGG", "iShares Core US Aggregate Bond", "400.0", "42000.00"),
    ],
    11: [
        ("NESN.SW", "Nestle SA", "55.0", "84000.00"),
        ("ROG.SW", "Roche Holding", "40.0", "122000.00"),
        ("VWRL.L", "Vanguard FTSE All-World", "45.0", "51000.00"),
        ("CHF", "Swiss Franc Cash", "9000.0", "9000.00"),
    ],
    12: [  # Theo — complaint thread; mid-size book
        ("ROG.SW", "Roche Holding", "38.0", "116000.00"),
        ("AGG", "iShares Core US Aggregate Bond", "350.0", "37000.00"),
        ("CHF", "Swiss Franc Cash", "31000.0", "31000.00"),
    ],
    13: [
        ("VWRL.L", "Vanguard FTSE All-World", "150.0", "169000.00"),
        ("NESN.SW", "Nestle SA", "70.0", "107000.00"),
        ("CHF", "Swiss Franc Cash", "19000.0", "19000.00"),
    ],
    14: [
        ("AGG", "iShares Core US Aggregate Bond", "450.0", "47000.00"),
        ("CHF", "Swiss Franc Cash", "88000.0", "88000.00"),
    ],
    15: [  # Iris — SLA breach; bond-heavy
        ("AGG", "iShares Core US Aggregate Bond", "800.0", "84000.00"),
        ("ROG.SW", "Roche Holding", "22.0", "67000.00"),
        ("CHF", "Swiss Franc Cash", "45000.0", "45000.00"),
    ],
}


def holdings_for_scenario(n: int) -> list[tuple[str, str, str, str]]:
    """Return the curated holdings pack for ``CLI-SCEN-NN``."""
    return list(SCENARIO_HOLDINGS.get(n, DEFAULT_HOLDINGS))


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
    scenario_n: int | None = None,
) -> Portfolio:
    """Insert one portfolio and holdings for the account.

    Each holding tuple is ``(symbol, name, quantity, market_value)``.
    Prefer ``scenario_n`` so curated scenarios stay distinct; pass ``holdings``
    only to override a pack explicitly.
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

    if holdings is not None:
        pack = holdings
    elif scenario_n is not None:
        pack = holdings_for_scenario(scenario_n)
    else:
        pack = DEFAULT_HOLDINGS

    for symbol, name, qty, value in pack:
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
