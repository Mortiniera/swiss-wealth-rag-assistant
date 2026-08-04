"""QA: curated CLI-SCEN-* seed data matches documented demo stories."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.models import Account, Client, ServiceRequest, Transaction
from app.database.session import SessionLocal
from app.services.client_read import get_client_by_ref


def _session():
    return SessionLocal()


def _client(session, code: str) -> Client:
    client = get_client_by_ref(session, code)
    assert client is not None, f"{code} missing from database — re-seed required"
    return client


def _open_service_requests(session, client: Client) -> list[ServiceRequest]:
    return list(
        session.scalars(
            select(ServiceRequest).where(
                ServiceRequest.client_id == client.id,
                ServiceRequest.status == "open",
            )
        ).all()
    )


def _pending_txns(session, client: Client) -> list[tuple[Transaction, str]]:
    rows = session.execute(
        select(Transaction, Account.account_code)
        .join(Account, Transaction.account_id == Account.id)
        .where(Account.client_id == client.id)
        .where(Transaction.status.in_(["pending", "pending_review"]))
    ).all()
    return list(rows)


def test_scen_01_expired_kyc_pending_transfer_and_hold():
    session = _session()
    try:
        client = _client(session, "CLI-SCEN-01")
        assert client.kyc_profile is not None
        assert client.kyc_profile.status == "expired"
        pending = _pending_txns(session, client)
        assert pending, "SCEN-01 expects a pending outbound transfer"
        accounts = session.scalars(
            select(Account)
            .where(Account.client_id == client.id)
            .options(selectinload(Account.restrictions))
        ).all()
        restricted = [a for a in accounts if (a.status or "").lower() == "restricted"]
        assert restricted, "SCEN-01 account should be restricted"
        active_holds = [
            r
            for a in restricted
            for r in a.restrictions
            if (r.status or "").lower() == "active"
        ]
        assert active_holds, "SCEN-01 expects an active KYC hold restriction"
        assert _open_service_requests(session, client), "SCEN-01 expects open SR"
    finally:
        session.close()


def test_scen_02_restricted_account_with_compliance_block():
    session = _session()
    try:
        client = _client(session, "CLI-SCEN-02")
        accounts = session.scalars(
            select(Account)
            .where(Account.client_id == client.id)
            .options(selectinload(Account.restrictions))
        ).all()
        restricted = [a for a in accounts if (a.status or "").lower() == "restricted"]
        assert restricted
        active = [
            r
            for a in restricted
            for r in a.restrictions
            if (r.status or "").lower() == "active"
        ]
        assert any(
            (r.restriction_type or "").lower() == "compliance_block" for r in active
        )
        assert _open_service_requests(session, client)
    finally:
        session.close()


def test_scen_03_pending_transfer_valid_kyc():
    session = _session()
    try:
        client = _client(session, "CLI-SCEN-03")
        assert client.kyc_profile is not None
        assert client.kyc_profile.status == "valid"
        assert _pending_txns(session, client)
        assert _open_service_requests(session, client)
    finally:
        session.close()


def test_scen_04_unusual_transaction_and_aml_sr():
    session = _session()
    try:
        client = _client(session, "CLI-SCEN-04")
        unusual = session.scalars(
            select(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .where(Account.client_id == client.id)
            .where(Transaction.is_unusual.is_(True))
        ).all()
        assert unusual, "SCEN-04 expects unusual transaction flag"
        open_srs = _open_service_requests(session, client)
        assert any(sr.request_type == "aml_review" for sr in open_srs)
    finally:
        session.close()


def test_scen_07_missing_suitability():
    session = _session()
    try:
        client = _client(session, "CLI-SCEN-07")
        assert client.suitability_profile is not None
        assert client.suitability_profile.status == "missing"
    finally:
        session.close()


def test_scen_15_sla_breach_service_request():
    session = _session()
    try:
        client = _client(session, "CLI-SCEN-15")
        open_srs = _open_service_requests(session, client)
        assert open_srs
        now = datetime.now(timezone.utc)
        assert any(sr.sla_due_at is not None and sr.sla_due_at < now for sr in open_srs)
    finally:
        session.close()


def test_all_scenario_clients_exist():
    session = _session()
    try:
        for n in range(1, 16):
            code = f"CLI-SCEN-{n:02d}"
            _client(session, code)
    finally:
        session.close()


def test_scenario_restricted_accounts_have_restriction_rows():
    session = _session()
    try:
        accounts = session.scalars(
            select(Account)
            .where(Account.account_code.like("ACC-SCEN-%"))
            .where(Account.status == "restricted")
            .options(selectinload(Account.restrictions))
        ).all()
        for account in accounts:
            active = [
                r for r in account.restrictions if (r.status or "").lower() == "active"
            ]
            assert active, f"{account.account_code} restricted without active rows"
    finally:
        session.close()
