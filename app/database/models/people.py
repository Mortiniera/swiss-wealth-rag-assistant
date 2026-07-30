"""People and coverage: roles, employees, households, clients, assignments."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.accounts import Account
    from app.database.models.compliance import (
        CommunicationPreference,
        KYCProfile,
        Restriction,
        SuitabilityProfile,
    )
    from app.database.models.operations import Interaction, ServiceRequest


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    employees: Mapped[list[Employee]] = relationship(back_populates="role")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    employee_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role: Mapped[Role] = relationship(back_populates="employees")
    assignments: Mapped[list[ClientAssignment]] = relationship(back_populates="employee")


class Household(Base):
    __tablename__ = "households"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    household_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)

    clients: Mapped[list[Client]] = relationship(back_populates="household")


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String(256), nullable=False)
    residency_country: Mapped[str] = mapped_column(String(2), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    household_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("households.id"), nullable=True
    )
    segment: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    household: Mapped[Optional[Household]] = relationship(back_populates="clients")
    assignments: Mapped[list[ClientAssignment]] = relationship(back_populates="client")
    accounts: Mapped[list[Account]] = relationship(back_populates="client")
    kyc_profile: Mapped[Optional[KYCProfile]] = relationship(
        back_populates="client", uselist=False
    )
    suitability_profile: Mapped[Optional[SuitabilityProfile]] = relationship(
        back_populates="client", uselist=False
    )
    communication_preference: Mapped[Optional[CommunicationPreference]] = relationship(
        back_populates="client", uselist=False
    )
    restrictions: Mapped[list[Restriction]] = relationship(back_populates="client")
    service_requests: Mapped[list[ServiceRequest]] = relationship(back_populates="client")
    interactions: Mapped[list[Interaction]] = relationship(back_populates="client")


class ClientAssignment(Base):
    __tablename__ = "client_assignments"
    __table_args__ = (
        UniqueConstraint("client_id", "employee_id", name="uq_client_employee"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clients.id"), nullable=False)
    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id"), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    client: Mapped[Client] = relationship(back_populates="assignments")
    employee: Mapped[Employee] = relationship(back_populates="assignments")
