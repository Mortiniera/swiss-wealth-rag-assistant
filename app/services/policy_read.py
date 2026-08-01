"""Read helpers for Helvetia policy documents in the knowledge store."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.knowledge import KnowledgeDocument
from app.schemas.policies import PolicyDetailOut, PolicySummaryOut


def build_policy_summary(doc: KnowledgeDocument) -> PolicySummaryOut:
    return PolicySummaryOut.model_validate(doc)


def build_policy_detail(doc: KnowledgeDocument) -> PolicyDetailOut:
    return PolicyDetailOut.model_validate(doc)


def list_policies(
    session: Session,
    *,
    active_only: bool = True,
) -> list[KnowledgeDocument]:
    """Return policy documents ordered by document_id."""
    stmt = select(KnowledgeDocument).order_by(KnowledgeDocument.document_id.asc())
    if active_only:
        stmt = stmt.where(KnowledgeDocument.status == "active")
    return list(session.scalars(stmt).all())


def get_policy_by_document_id(
    session: Session, document_id: str
) -> KnowledgeDocument | None:
    """Resolve a policy by stable ``document_id`` (e.g. ``POL-KYC-001``)."""
    return session.scalar(
        select(KnowledgeDocument).where(KnowledgeDocument.document_id == document_id)
    )
