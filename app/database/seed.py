"""Truncate domain tables and populate synthetic Helvetia banking data."""

from __future__ import annotations

import random
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.models import (
    Account,
    AuditEvent,
    Client,
    ClientAssignment,
    CommunicationPreference,
    Employee,
    Holding,
    Household,
    Interaction,
    KYCProfile,
    Portfolio,
    Role,
    ServiceRequest,
    SuitabilityProfile,
    Transaction,
)
from app.database.seed_scenarios import apply_scenario_overrides

TABLES_IN_DELETE_ORDER = [
    "audit_events",
    "interactions",
    "holdings",
    "restrictions",
    "transactions",
    "service_requests",
    "portfolios",
    "communication_preferences",
    "suitability_profiles",
    "kyc_profiles",
    "accounts",
    "client_assignments",
    "clients",
    "employees",
    "households",
    "roles",
]


def reset_database(session: Session) -> None:
    """Delete all domain rows without dropping schema."""
    session.execute(
        text(
            "TRUNCATE TABLE "
            + ", ".join(TABLES_IN_DELETE_ORDER)
            + " RESTART IDENTITY CASCADE"
        )
    )
    session.commit()


FIRST_NAMES = [
    "Elena", "Marcus", "Sophie", "Jonas", "Clara", "Noah", "Amelie", "Luca",
    "Nina", "Felix", "Helena", "Adrian", "Maya", "Theo", "Lea", "David",
    "Iris", "Simon", "Paula", "Erik",
]
LAST_NAMES = [
    "Weber", "Keller", "Meier", "Brunner", "Fischer", "Favre", "Rossi",
    "Schneider", "Bernard", "Hoffmann", "Dubois", "Graf", "Moreau", "Baumann",
    "Petit", "Steiner", "Blanc", "Zimmermann", "Martin", "Koch",
]
COUNTRIES = ["CH", "FR", "DE", "IT", "GB", "US", "SG", "AE"]
CURRENCIES = ["CHF", "EUR", "USD"]
ASSETS = [
    ("CHF", "Swiss Franc Cash"),
    ("NESN.SW", "Nestle SA"),
    ("ROG.SW", "Roche Holding"),
    ("VWRL.L", "Vanguard FTSE All-World"),
    ("AGG", "iShares Core US Aggregate Bond"),
]


def _now_utc() -> datetime:
    """Return the current UTC timestamp used as the seed run clock."""
    return datetime.now(timezone.utc)


def _seed_roles(session: Session) -> dict[str, Role]:
    """Insert roles and return them keyed by code."""
    roles = [
        Role(id=uuid.uuid4(), code="relationship_manager", name="Relationship Manager"),
        Role(id=uuid.uuid4(), code="client_service", name="Client Service"),
        Role(id=uuid.uuid4(), code="compliance_viewer", name="Compliance Viewer"),
    ]
    session.add_all(roles)
    session.flush()
    return {r.code: r for r in roles}


def _seed_employees(
    session: Session,
    role_by_code: dict[str, Role],
    *,
    employee_count: int,
) -> tuple[list[Employee], list[Employee]]:
    """Insert employees; return (all employees, relationship managers only)."""
    employees: list[Employee] = []
    for i in range(1, employee_count + 1):
        if i <= employee_count - 2:
            role = role_by_code["relationship_manager"]
        elif i == employee_count - 1:
            role = role_by_code["client_service"]
        else:
            role = role_by_code["compliance_viewer"]

        fn = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        ln = LAST_NAMES[(i * 3) % len(LAST_NAMES)]
        employees.append(
            Employee(
                id=uuid.uuid4(),
                employee_code=f"EMP-{i:04d}",
                full_name=f"{fn} {ln}",
                email=f"{fn.lower()}.{ln.lower()}{i}@helvetia-private.example",
                role_id=role.id,
                is_active=True,
            )
        )

    session.add_all(employees)
    session.flush()
    rms = [
        e for e in employees if e.role_id == role_by_code["relationship_manager"].id
    ]
    return employees, rms


def _seed_households(session: Session, *, household_count: int) -> list[Household]:
    """Insert synthetic households."""
    households = [
        Household(
            id=uuid.uuid4(),
            household_code=f"HH-{i:04d}",
            display_name=f"{LAST_NAMES[(i - 1) % len(LAST_NAMES)]} Family",
        )
        for i in range(1, household_count + 1)
    ]
    session.add_all(households)
    session.flush()
    return households


def _seed_clients(
    session: Session,
    rng: random.Random,
    households: list[Household],
    *,
    client_count: int,
    now: datetime,
) -> list[Client]:
    """Insert clients with deterministic CLI-###### codes."""
    clients: list[Client] = []
    for n in range(1, client_count + 1):
        fn = FIRST_NAMES[rng.randrange(len(FIRST_NAMES))]
        ln = LAST_NAMES[rng.randrange(len(LAST_NAMES))]
        hh = households[rng.randrange(len(households))] if rng.random() < 0.7 else None
        clients.append(
            Client(
                id=uuid.uuid4(),
                client_code=f"CLI-{n:06d}",
                full_name=f"{fn} {ln}",
                email=f"client.{n:06d}@clients.helvetia.example",
                residency_country=rng.choice(COUNTRIES),
                status=rng.choice(
                    ["active", "active", "active", "dormant", "onboarding"]
                ),
                household_id=hh.id if hh else None,
                segment=rng.choice(["hnwi", "hnwi", "uhnw"]),
                created_at=now - timedelta(days=rng.randint(30, 2000)),
            )
        )
    session.add_all(clients)
    session.flush()
    return clients


def _seed_assignments(
    session: Session,
    rng: random.Random,
    clients: list[Client],
    rms: list[Employee],
) -> None:
    """Insert a primary ClientAssignment for each client."""
    for client in clients:
        session.add(
            ClientAssignment(
                id=uuid.uuid4(),
                client_id=client.id,
                employee_id=rms[rng.randrange(len(rms))].id,
                is_primary=True,
                assigned_at=client.created_at,
            )
        )


def _seed_accounts(
    session: Session,
    rng: random.Random,
    clients: list[Client],
) -> list[Account]:
    """Insert one to four accounts per client."""
    accounts: list[Account] = []
    account_seq = 1
    for client in clients:
        for _ in range(rng.randint(1, 4)):
            accounts.append(
                Account(
                    id=uuid.uuid4(),
                    account_code=f"ACC-{account_seq:06d}",
                    client_id=client.id,
                    account_type=rng.choice(["current", "custody", "custody"]),
                    currency=rng.choice(CURRENCIES),
                    status=rng.choice(["open", "open", "open", "restricted"]),
                    iban_synthetic=f"CH93HELVE{account_seq:012d}",
                    opened_at=client.created_at + timedelta(days=rng.randint(1, 60)),
                )
            )
            account_seq += 1
    session.add_all(accounts)
    session.flush()
    return accounts


def _seed_portfolios_and_holdings(
    session: Session,
    rng: random.Random,
    accounts: list[Account],
    *,
    now: datetime,
) -> None:
    """Insert one portfolio and a random holding set per account."""
    for account in accounts:
        portfolio = Portfolio(
            id=uuid.uuid4(),
            account_id=account.id,
            name=f"Portfolio {account.account_code}",
            base_currency=account.currency,
            as_of=now - timedelta(days=1),
        )
        session.add(portfolio)
        session.flush()

        for asset_symbol, asset_name in rng.sample(ASSETS, k=rng.randint(2, 4)):
            session.add(
                Holding(
                    id=uuid.uuid4(),
                    portfolio_id=portfolio.id,
                    asset_symbol=asset_symbol,
                    asset_name=asset_name,
                    quantity=Decimal(str(round(rng.uniform(1, 500), 4))),
                    market_value=Decimal(
                        str(round(rng.uniform(5_000, 2_500_000), 2))
                    ),
                    currency=account.currency,
                )
            )


def _seed_transactions(
    session: Session,
    rng: random.Random,
    accounts: list[Account],
    *,
    now: datetime,
) -> int:
    """Insert booked transaction history per account; return transaction count."""
    txn_seq = 1
    for account in accounts:
        for _ in range(rng.randint(3, 10)):
            booked = now - timedelta(days=rng.randint(1, 400))
            session.add(
                Transaction(
                    id=uuid.uuid4(),
                    account_id=account.id,
                    transaction_code=f"TXN-{txn_seq:06d}",
                    txn_type=rng.choice(
                        ["transfer_out", "transfer_in", "fee", "dividend", "trade"]
                    ),
                    amount=Decimal(str(round(rng.uniform(100, 50_000), 2))),
                    currency=account.currency,
                    status="booked",
                    booked_at=booked,
                    value_date=booked,
                    counterparty_name=f"CP-{rng.randint(1, 200):03d}",
                    description="Booked synthetic transaction",
                    delay_reason_code=None,
                    is_unusual=False,
                    created_at=booked,
                )
            )
            txn_seq += 1
    return txn_seq - 1


def kyc_document_expiry_for_status(
    status: str,
    *,
    today: date,
    rng: random.Random,
) -> date:
    """
    Pick a passport expiry that matches the KYC status story.

    ``expired`` always lands in the past; ``valid`` always in the future;
    ``incomplete`` / ``invalid`` stay near-term (package gap, not expiry theatre).
    """
    normalized = (status or "").lower()
    if normalized == "expired":
        return today - timedelta(days=rng.randint(1, 180))
    if normalized in {"incomplete", "invalid"}:
        return today + timedelta(days=rng.randint(7, 60))
    if normalized == "refresh_due":
        return today + timedelta(days=rng.randint(1, 45))
    return today + timedelta(days=rng.randint(90, 800))


def _seed_client_profiles(
    session: Session,
    rng: random.Random,
    clients: list[Client],
    *,
    now: datetime,
) -> None:
    """Insert KYC, suitability, and communication preference rows per client."""
    today = now.date()
    for client in clients:
        kyc_status = rng.choice(
            ["valid", "valid", "valid", "expired", "incomplete"]
        )
        session.add(
            KYCProfile(
                id=uuid.uuid4(),
                client_id=client.id,
                status=kyc_status,
                document_type="passport",
                document_expiry=kyc_document_expiry_for_status(
                    kyc_status, today=today, rng=rng
                ),
                last_reviewed_at=now - timedelta(days=rng.randint(10, 400)),
                notes="Synthetic KYC profile",
            )
        )

        suit_status = rng.choice(["complete", "complete", "missing", "outdated"])
        session.add(
            SuitabilityProfile(
                id=uuid.uuid4(),
                client_id=client.id,
                status=suit_status,
                risk_profile=(
                    None
                    if suit_status == "missing"
                    else rng.choice(["conservative", "balanced", "growth"])
                ),
                completed_at=(
                    None
                    if suit_status == "missing"
                    else now - timedelta(days=rng.randint(30, 600))
                ),
            )
        )

        session.add(
            CommunicationPreference(
                id=uuid.uuid4(),
                client_id=client.id,
                preferred_channel=rng.choice(
                    ["email", "phone", "secure_message", "letter"]
                ),
                marketing_opt_in=rng.random() < 0.3,
                cross_border_ok=rng.random() < 0.85,
                language=rng.choice(["en", "fr", "de"]),
            )
        )


def _seed_ops_activity(
    session: Session,
    rng: random.Random,
    clients: list[Client],
    employees: list[Employee],
    *,
    now: datetime,
    fraction: float = 0.12,
) -> dict[str, int]:
    """
    Sprinkle open service requests + interactions on a subset of bulk clients.

    Curated CLI-SCEN-* rows still own the flagship ticket stories; this keeps
    random book browsing from looking empty in SR / interaction panels.
    """
    if not clients or not employees:
        return {"service_requests": 0, "interactions": 0}

    assignees = employees
    sr_count = 0
    ix_count = 0
    seq = 1

    for client in clients:
        if rng.random() >= fraction:
            continue

        assignee = rng.choice(assignees)
        request_type = rng.choice(
            ["enquiry", "follow_up", "complaint", "kyc_refresh"]
        )
        subject = {
            "enquiry": "General account enquiry",
            "follow_up": "Ops follow-up required",
            "complaint": "Fee or service complaint",
            "kyc_refresh": "KYC document refresh chase",
        }[request_type]

        sr = ServiceRequest(
            id=uuid.uuid4(),
            request_code=f"SRQ-BULK-{seq:05d}",
            client_id=client.id,
            request_type=request_type,
            status="open",
            priority=rng.choice(["low", "medium", "high"]),
            subject=subject,
            opened_at=now - timedelta(days=rng.randint(2, 40)),
            sla_due_at=now + timedelta(days=rng.randint(-3, 14)),
            resolved_at=None,
            assigned_employee_id=assignee.id,
        )
        session.add(sr)
        session.flush()
        sr_count += 1

        inbound = rng.random() < 0.55
        interaction = Interaction(
            id=uuid.uuid4(),
            client_id=client.id,
            employee_id=None if inbound else assignee.id,
            channel=rng.choice(["email", "phone", "secure_message"]),
            direction="inbound" if inbound else "outbound",
            subject=f"Note on {subject.lower()}",
            summary=(
                "Client reached out; case remains open pending ops review."
                if inbound
                else "Bank noted follow-up on the open service request."
            ),
            occurred_at=now - timedelta(days=rng.randint(1, 20)),
            related_service_request_id=sr.id,
            status="awaiting_reply" if inbound else "logged",
        )
        session.add(interaction)
        ix_count += 1
        seq += 1

    return {"service_requests": sr_count, "interactions": ix_count}


def _seed_audit_marker(
    session: Session,
    *,
    actor: Employee,
    rng_seed: int,
    client_count: int,
    now: datetime,
) -> None:
    """Insert an audit event describing this seed run."""
    session.add(
        AuditEvent(
            id=uuid.uuid4(),
            event_type="scenario_seed",
            actor_employee_id=actor.id,
            entity_type="database",
            entity_id=None,
            payload_json={
                "rng_seed": rng_seed,
                "client_count": client_count,
                "phase": "base",
            },
            created_at=now,
        )
    )


def seed_database(
    session: Session,
    *,
    rng_seed: int = 42,
    client_count: int = 500,
    household_count: int = 75,
    employee_count: int = 12,
) -> dict[str, int]:
    """Populate synthetic domain data and return insertion counts.

    Expects an empty domain (call ``reset_database`` first when reseeding).
    Insertion order: roles, employees, households, bulk clients, then
    curated CLI-SCEN-* overrides.
    """
    rng = random.Random(rng_seed)
    now = _now_utc()

    role_by_code = _seed_roles(session)
    employees, rms = _seed_employees(
        session, role_by_code, employee_count=employee_count
    )
    client_service = next(
        e for e in employees if e.role_id == role_by_code["client_service"].id
    )
    households = _seed_households(session, household_count=household_count)

    clients = _seed_clients(
        session, rng, households, client_count=client_count, now=now
    )
    _seed_assignments(session, rng, clients, rms)

    accounts = _seed_accounts(session, rng, clients)
    _seed_portfolios_and_holdings(session, rng, accounts, now=now)
    txn_count = _seed_transactions(session, rng, accounts, now=now)

    _seed_client_profiles(session, rng, clients, now=now)
    ops_stats = _seed_ops_activity(session, rng, clients, employees, now=now)

    _seed_audit_marker(
        session,
        actor=employees[0],
        rng_seed=rng_seed,
        client_count=client_count,
        now=now,
    )

    scenario_stats = apply_scenario_overrides(
        session,
        rms=rms,
        client_service=client_service,
        now=now,
    )

    session.commit()

    return {
        "roles": len(role_by_code),
        "employees": len(employees),
        "households": len(households),
        "clients": len(clients) + scenario_stats["scenario_clients"],
        "accounts": len(accounts) + scenario_stats["scenario_accounts"],
        "transactions": txn_count,
        "service_requests": ops_stats["service_requests"],
        "interactions": ops_stats["interactions"],
        "scenario_clients": scenario_stats["scenario_clients"],
    }
