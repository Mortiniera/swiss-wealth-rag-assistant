"""Accounts, portfolios, holdings, and transactions."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.compliance import Restriction
    from app.database.models.people import Client


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False)
    account_type: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    iban_synthetic: Mapped[str] = mapped_column(String(64), nullable=False)
    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    client: Mapped[Client] = relationship(back_populates="accounts")
    portfolio: Mapped[Optional[Portfolio]] = relationship(
        back_populates="account", uselist=False
    )
    transactions: Mapped[list[Transaction]] = relationship(back_populates="account")
    restrictions: Mapped[list[Restriction]] = relationship(back_populates="account")


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id"), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    as_of: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    account: Mapped[Account] = relationship(back_populates="portfolio")
    holdings: Mapped[list[Holding]] = relationship(back_populates="portfolio")


class Holding(Base):
    __tablename__ = "holdings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    portfolio_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("portfolios.id"), nullable=False
    )
    asset_symbol: Mapped[str] = mapped_column(String(64), nullable=False)
    asset_name: Mapped[str] = mapped_column(String(256), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    market_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

    portfolio: Mapped[Portfolio] = relationship(back_populates="holdings")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    account_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("accounts.id"), nullable=False
    )
    transaction_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    txn_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    booked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    value_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    counterparty_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    delay_reason_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    is_unusual: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    account: Mapped[Account] = relationship(back_populates="transactions")
