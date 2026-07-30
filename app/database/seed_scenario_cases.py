"""Individual curated scenario seeders (SCEN-01 .. SCEN-15)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.database.models import Employee
from app.database.scenario_builders import (
    assign_rm,
    make_account,
    make_client,
    make_comms,
    make_interaction,
    make_kyc,
    make_portfolio_with_holdings,
    make_restriction,
    make_service_request,
    make_suitability,
    make_txn,
)

SCENARIO_COUNT = 15


@dataclass(frozen=True)
class ScenarioContext:
    """Shared session and actors passed into each scenario seeder."""

    session: Session
    rm: Employee
    client_service: Employee
    now: datetime


def seed_scen_01(ctx: ScenarioContext) -> None:
    """Expired KYC with pending transfer held on a KYC hold (UC-1)."""
    session, rm, cs, now = ctx.session, ctx.rm, ctx.client_service, ctx.now
    client = make_client(
        session, 1, full_name="Helena Vogt", status="active", residency_country="CH", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 1, client, status="restricted")
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="expired",
        document_expiry=date.today() - timedelta(days=45),
        now=now,
        notes="Passport expired; refresh requested",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client)
    make_txn(
        session,
        1,
        account,
        status="pending",
        amount="85000.00",
        now=now,
        delay_reason_code="kyc_expired",
        description="Outbound transfer held pending KYC refresh",
        booked_offset_days=2,
    )
    make_restriction(
        session,
        1,
        client=client,
        account=account,
        restriction_type="kyc_hold",
        reason_code="kyc_expired",
        now=now,
        notes="KYC hold blocking outbound transfers",
    )
    request = make_service_request(
        session,
        1,
        client,
        request_type="kyc_refresh",
        subject="Passport refresh for outbound transfer",
        now=now,
        priority="high",
        sla_due_at=now + timedelta(days=5),
        assigned=cs,
    )
    make_interaction(
        session,
        client,
        employee=rm,
        channel="secure_message",
        direction="outbound",
        subject="KYC document request",
        summary="Requested updated passport copy before releasing pending transfer.",
        now=now,
        related=request,
        days_ago=8,
    )


def seed_scen_02(ctx: ScenarioContext) -> None:
    """Active compliance block on a restricted account."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session, 2, full_name="Marcus Keller", status="active", residency_country="CH", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 2, client, status="restricted")
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=400),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client)
    make_restriction(
        session,
        2,
        client=client,
        account=account,
        restriction_type="compliance_block",
        reason_code="manual_review",
        now=now,
        notes="Manual compliance review block",
    )


def seed_scen_03(ctx: ScenarioContext) -> None:
    """Pending outbound transfer delayed for ops review with valid KYC."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session, 3, full_name="Sophie Meier", status="active", residency_country="CH", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 3, client)
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=500),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client)
    make_txn(
        session,
        3,
        account,
        status="pending",
        amount="42000.00",
        now=now,
        delay_reason_code="ops_review",
        description="Outbound transfer pending operational review",
        booked_offset_days=1,
    )


def seed_scen_04(ctx: ScenarioContext) -> None:
    """Booked cash movement flagged as unusual."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session, 4, full_name="Jonas Brunner", status="active", residency_country="DE", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 4, client, currency="EUR")
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=300),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client)
    make_txn(
        session,
        4,
        account,
        status="booked",
        amount="275000.00",
        now=now,
        is_unusual=True,
        description="Unusual cash pattern vs client baseline",
        booked_offset_days=4,
    )


def seed_scen_05(ctx: ScenarioContext) -> None:
    """Incomplete onboarding with missing suitability and incomplete KYC."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session,
        5,
        full_name="Clara Favre",
        status="onboarding",
        residency_country="CH",
        now=now,
    )
    assign_rm(session, client, rm)
    account = make_account(session, 5, client, account_type="custody")
    make_portfolio_with_holdings(
        session,
        account,
        now=now,
        holdings=[("CHF", "Swiss Franc Cash", "1000.0", "1000.00")],
    )
    make_kyc(
        session,
        client,
        status="incomplete",
        document_expiry=date.today() + timedelta(days=30),
        now=now,
        notes="Onboarding KYC package incomplete",
    )
    make_suitability(session, client, status="missing", now=now)
    make_comms(session, client, preferred_channel="email")


def seed_scen_06(ctx: ScenarioContext) -> None:
    """Open complaint ticket still within SLA, with prior interaction history."""
    session, rm, cs, now = ctx.session, ctx.rm, ctx.client_service, ctx.now
    client = make_client(
        session, 6, full_name="Noah Rossi", status="active", residency_country="IT", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 6, client, currency="EUR")
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=200),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client)
    request = make_service_request(
        session,
        6,
        client,
        request_type="complaint",
        subject="Fee dispute on custody account",
        now=now,
        priority="high",
        sla_due_at=now + timedelta(days=3),
        assigned=cs,
    )
    make_interaction(
        session,
        client,
        employee=cs,
        channel="phone",
        direction="inbound",
        subject="Complaint call — custody fees",
        summary="Client disputes recent custody fee; awaits written explanation.",
        now=now,
        related=request,
        days_ago=10,
    )


def seed_scen_07(ctx: ScenarioContext) -> None:
    """Active client with valid KYC but missing suitability questionnaire."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session, 7, full_name="Amelie Schneider", status="active", residency_country="CH", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 7, client)
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=600),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="missing", now=now)
    make_comms(session, client)


def seed_scen_08(ctx: ScenarioContext) -> None:
    """US resident with cross-border communication declined."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session, 8, full_name="Luca Hoffmann", status="active", residency_country="US", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 8, client, currency="USD")
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=350),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client, preferred_channel="email", cross_border_ok=False, language="en")
    make_interaction(
        session,
        client,
        employee=rm,
        channel="email",
        direction="outbound",
        subject="Cross-border contact declined",
        summary="Outbound contact constrained: cross_border_ok=false for US residency.",
        now=now,
        status="logged",
        days_ago=6,
    )


def seed_scen_09(ctx: ScenarioContext) -> None:
    """Dormant relationship with limited recent activity."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session, 9, full_name="Nina Dubois", status="dormant", residency_country="FR", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 9, client, currency="EUR")
    make_portfolio_with_holdings(
        session,
        account,
        now=now,
        holdings=[
            ("VWRL.L", "Vanguard FTSE All-World", "80.0", "95000.00"),
            ("CHF", "Swiss Franc Cash", "500.0", "500.00"),
        ],
    )
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=100),
        now=now,
        notes="Valid KYC; relationship dormant",
    )
    make_suitability(session, client, status="outdated", now=now, risk_profile="conservative")
    make_comms(session, client, preferred_channel="letter", language="fr")


def seed_scen_10(ctx: ScenarioContext) -> None:
    """Portfolio performance enquiry with holdings available for inspection."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session, 10, full_name="Felix Graf", status="active", residency_country="CH", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 10, client)
    make_portfolio_with_holdings(
        session,
        account,
        now=now,
        holdings=[
            ("NESN.SW", "Nestle SA", "200.0", "210000.00"),
            ("ROG.SW", "Roche Holding", "30.0", "88000.00"),
            ("AGG", "iShares Core US Aggregate Bond", "400.0", "42000.00"),
        ],
    )
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=450),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now, risk_profile="growth")
    make_comms(session, client)
    request = make_service_request(
        session,
        10,
        client,
        request_type="enquiry",
        subject="Portfolio performance concern",
        now=now,
        priority="medium",
        sla_due_at=now + timedelta(days=7),
        assigned=rm,
    )
    make_interaction(
        session,
        client,
        employee=rm,
        channel="phone",
        direction="inbound",
        subject="Client asks about portfolio decline",
        summary="Client enquired about recent mark-to-market weakness vs peers.",
        now=now,
        related=request,
        days_ago=3,
    )


def seed_scen_11(ctx: ScenarioContext) -> None:
    """Preferred channel conflicts with how follow-up was planned."""
    session, rm, cs, now = ctx.session, ctx.rm, ctx.client_service, ctx.now
    client = make_client(
        session, 11, full_name="Maya Moreau", status="active", residency_country="CH", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 11, client)
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=280),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client, preferred_channel="letter")
    request = make_service_request(
        session,
        11,
        client,
        request_type="follow_up",
        subject="Phone callback requested by operations",
        now=now,
        priority="medium",
        sla_due_at=now + timedelta(days=4),
        assigned=cs,
    )
    make_interaction(
        session,
        client,
        employee=cs,
        channel="phone",
        direction="outbound",
        subject="Channel conflict noted",
        summary="Ops planned phone follow-up but preferred_channel is letter.",
        now=now,
        related=request,
        days_ago=2,
    )


def seed_scen_12(ctx: ScenarioContext) -> None:
    """Inbound client email awaiting reply, linked to an open request."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session, 12, full_name="Theo Baumann", status="active", residency_country="CH", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 12, client)
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=320),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client, preferred_channel="email")
    request = make_service_request(
        session,
        12,
        client,
        request_type="enquiry",
        subject="Unanswered client email on statement discrepancy",
        now=now,
        priority="high",
        sla_due_at=now + timedelta(days=2),
        assigned=rm,
    )
    make_interaction(
        session,
        client,
        employee=None,
        channel="email",
        direction="inbound",
        subject="Statement discrepancy question",
        summary="Client emailed about a statement line; awaiting bank reply.",
        now=now,
        status="awaiting_reply",
        related=request,
        days_ago=4,
    )


def seed_scen_13(ctx: ScenarioContext) -> None:
    """High-value booked cash transfer for UHNW review."""
    session, rm, now = ctx.session, ctx.rm, ctx.now
    client = make_client(
        session,
        13,
        full_name="Lea Petit",
        status="active",
        residency_country="CH",
        now=now,
        segment="uhnw",
    )
    assign_rm(session, client, rm)
    account = make_account(session, 13, client)
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=700),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now, risk_profile="growth")
    make_comms(session, client)
    make_txn(
        session,
        13,
        account,
        status="booked",
        amount="2500000.00",
        now=now,
        is_unusual=True,
        description="High-value booked cash transfer",
        booked_offset_days=2,
    )


def seed_scen_14(ctx: ScenarioContext) -> None:
    """Failed identity document upload with invalid KYC and open ticket."""
    session, rm, cs, now = ctx.session, ctx.rm, ctx.client_service, ctx.now
    client = make_client(
        session, 14, full_name="David Steiner", status="active", residency_country="CH", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 14, client)
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="invalid",
        document_expiry=date.today() + timedelta(days=10),
        now=now,
        notes="Document upload failed — file unreadable / rejected",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client)
    request = make_service_request(
        session,
        14,
        client,
        request_type="document_upload",
        subject="Failed identity document upload",
        now=now,
        priority="high",
        sla_due_at=now + timedelta(days=3),
        assigned=cs,
    )
    make_interaction(
        session,
        client,
        employee=cs,
        channel="secure_message",
        direction="outbound",
        subject="Upload failure notice",
        summary="Informed client that passport scan upload failed validation.",
        now=now,
        related=request,
        days_ago=1,
    )


def seed_scen_15(ctx: ScenarioContext) -> None:
    """Open service request past its SLA due date."""
    session, rm, cs, now = ctx.session, ctx.rm, ctx.client_service, ctx.now
    client = make_client(
        session, 15, full_name="Iris Blanc", status="active", residency_country="CH", now=now
    )
    assign_rm(session, client, rm)
    account = make_account(session, 15, client)
    make_portfolio_with_holdings(session, account, now=now)
    make_kyc(
        session,
        client,
        status="valid",
        document_expiry=date.today() + timedelta(days=380),
        now=now,
        notes="Valid KYC",
    )
    make_suitability(session, client, status="complete", now=now)
    make_comms(session, client)
    request = make_service_request(
        session,
        15,
        client,
        request_type="complaint",
        subject="Escalated fee complaint past SLA",
        now=now,
        priority="high",
        sla_due_at=now - timedelta(days=5),
        assigned=cs,
    )
    make_interaction(
        session,
        client,
        employee=cs,
        channel="email",
        direction="inbound",
        subject="Follow-up on overdue complaint",
        summary="Client chased unresolved fee complaint after SLA due date.",
        now=now,
        related=request,
        days_ago=2,
    )


SCENARIO_SEEDERS = (
    seed_scen_01,
    seed_scen_02,
    seed_scen_03,
    seed_scen_04,
    seed_scen_05,
    seed_scen_06,
    seed_scen_07,
    seed_scen_08,
    seed_scen_09,
    seed_scen_10,
    seed_scen_11,
    seed_scen_12,
    seed_scen_13,
    seed_scen_14,
    seed_scen_15,
)
