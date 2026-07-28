"""ORM models package — import submodules so tables register on Base.metadata."""

from app.database.models.accounts import Account, Holding, Portfolio, Transaction
from app.database.models.compliance import (
    CommunicationPreference,
    KYCProfile,
    Restriction,
    SuitabilityProfile,
)
from app.database.models.operations import AuditEvent, Interaction, ServiceRequest
from app.database.models.people import (
    Client,
    ClientAssignment,
    Employee,
    Household,
    Role,
)

__all__ = [
    "Role",
    "Employee",
    "Household",
    "Client",
    "ClientAssignment",
    "Account",
    "Portfolio",
    "Holding",
    "Transaction",
    "KYCProfile",
    "SuitabilityProfile",
    "CommunicationPreference",
    "Restriction",
    "ServiceRequest",
    "Interaction",
    "AuditEvent",
]
