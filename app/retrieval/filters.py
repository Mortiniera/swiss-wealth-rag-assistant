"""Shared SQL filter clauses for knowledge retrieval."""

from __future__ import annotations

from sqlalchemy import ColumnElement, and_

from app.database.models.knowledge import KnowledgeDocument
from app.retrieval.types import RetrievalFilters


def document_filter_clause(filters: RetrievalFilters) -> ColumnElement[bool]:
    """Build AND-ed SQLAlchemy predicates for document metadata filters."""
    clauses: list[ColumnElement[bool]] = [
        KnowledgeDocument.status == filters.status,
    ]
    if filters.role is not None:
        clauses.append(KnowledgeDocument.allowed_roles.any(filters.role))
    if filters.jurisdiction is not None:
        clauses.append(KnowledgeDocument.jurisdiction == filters.jurisdiction)
    if filters.category is not None:
        clauses.append(KnowledgeDocument.category == filters.category)
    return and_(*clauses)
