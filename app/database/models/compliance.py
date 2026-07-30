"""KYC, suitability, communication preferences, and restrictions."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.accounts import Account
    from app.database.models.people import Client


class KYCProfile(Base):
    __tablename__ = "kyc_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    document_type: Mapped[str] = mapped_column(String(64), nullable=False)
    document_expiry: Mapped[date] = mapped_column(Date, nullable=False)
    last_reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    client: Mapped[Client] = relationship(back_populates="kyc_profile")


class SuitabilityProfile(Base):
    __tablename__ = "suitability_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"), unique=True, nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    risk_profile: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    client: Mapped[Client] = relationship(back_populates="suitability_profile")


class CommunicationPreference(Base):
    __tablename__ = "communication_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"), unique=True, nullable=False
    )
    preferred_channel: Mapped[str] = mapped_column(String(32), nullable=False)
    marketing_opt_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cross_border_ok: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    language: Mapped[str] = mapped_column(String(8), nullable=False)

    client: Mapped[Client] = relationship(back_populates="communication_preference")


class Restriction(Base):
    __tablename__ = "restrictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("clients.id"), nullable=True
    )
    account_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("accounts.id"), nullable=True
    )
    restriction_type: Mapped[str] = mapped_column(String(64), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    client: Mapped[Optional[Client]] = relationship(back_populates="restrictions")
    account: Mapped[Optional[Account]] = relationship(back_populates="restrictions")
