"""Pydantic schemas for read-only Helvetia client verification APIs."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class KYCProfileOut(BaseModel):
    """KYC document state for a client."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    document_type: str
    document_expiry: date
    last_reviewed_at: datetime | None = None
    notes: str | None = None


class SuitabilityProfileOut(BaseModel):
    """Suitability questionnaire state for a client."""

    model_config = ConfigDict(from_attributes=True)

    status: str
    risk_profile: str | None = None
    completed_at: datetime | None = None


class CommunicationPreferenceOut(BaseModel):
    """Client communication channel preferences."""

    model_config = ConfigDict(from_attributes=True)

    preferred_channel: str
    marketing_opt_in: bool
    cross_border_ok: bool
    language: str


class PrimaryAssignmentOut(BaseModel):
    """Primary relationship-manager coverage for a client."""

    employee_code: str
    full_name: str
    email: str


class ClientOut(BaseModel):
    """Client profile with compliance and coverage context."""

    id: uuid.UUID
    client_code: str
    full_name: str
    email: str
    residency_country: str
    status: str
    segment: str
    household_code: str | None = None
    created_at: datetime
    kyc_profile: KYCProfileOut | None = None
    suitability_profile: SuitabilityProfileOut | None = None
    communication_preference: CommunicationPreferenceOut | None = None
    primary_assignment: PrimaryAssignmentOut | None = None


class RestrictionOut(BaseModel):
    """Active or historical restriction on a client or account."""

    model_config = ConfigDict(from_attributes=True)

    restriction_type: str
    reason_code: str
    status: str
    effective_from: datetime
    effective_to: datetime | None = None
    notes: str | None = None


class AccountOut(BaseModel):
    """Client account with linked restrictions."""

    id: uuid.UUID
    account_code: str
    account_type: str
    currency: str
    status: str
    iban_synthetic: str
    opened_at: datetime
    restrictions: list[RestrictionOut] = Field(default_factory=list)


class HoldingOut(BaseModel):
    """Single holding line in a custody portfolio."""

    asset_symbol: str
    asset_name: str
    quantity: Decimal
    market_value: Decimal
    currency: str


class AccountSummaryOut(BaseModel):
    """Account snapshot with optional portfolio holdings."""

    account_code: str
    account_type: str
    currency: str
    status: str
    portfolio_name: str | None = None
    portfolio_as_of: datetime | None = None
    base_currency: str | None = None
    holdings: list[HoldingOut] = Field(default_factory=list)


class TransactionOut(BaseModel):
    """Booked or pending movement on a client account."""

    id: uuid.UUID
    transaction_code: str
    account_code: str
    txn_type: str
    amount: Decimal
    currency: str
    status: str
    booked_at: datetime | None = None
    value_date: datetime | None = None
    counterparty_name: str | None = None
    description: str
    delay_reason_code: str | None = None
    is_unusual: bool
    created_at: datetime


class InteractionOut(BaseModel):
    """Logged client interaction."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    channel: str
    direction: str
    subject: str
    summary: str
    occurred_at: datetime
    status: str
    employee_code: str | None = None
    related_request_code: str | None = None


class ServiceRequestOut(BaseModel):
    """Open or resolved client service request."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    request_code: str
    request_type: str
    status: str
    priority: str
    subject: str
    opened_at: datetime
    sla_due_at: datetime | None = None
    resolved_at: datetime | None = None
    assigned_employee_code: str | None = None
