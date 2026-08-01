"""Unit checks for knowledge / pgvector ORM models."""

from __future__ import annotations

from app.database.base import Base
from app.database.models.knowledge import (
    EMBEDDING_DIMENSIONS,
    KnowledgeChunk,
    KnowledgeDocument,
)


def test_embedding_dimensions_match_openai_small_default() -> None:
    assert EMBEDDING_DIMENSIONS == 1536


def test_knowledge_tables_registered_on_metadata() -> None:
    assert "knowledge_documents" in Base.metadata.tables
    assert "knowledge_chunks" in Base.metadata.tables


def test_knowledge_document_columns() -> None:
    cols = set(KnowledgeDocument.__table__.columns.keys())
    expected = {
        "id",
        "document_id",
        "title",
        "department",
        "doc_type",
        "category",
        "jurisdiction",
        "allowed_roles",
        "effective_date",
        "version",
        "status",
        "confidentiality",
        "supersedes_document_id",
        "source_path",
        "body",
        "created_at",
        "updated_at",
    }
    assert expected.issubset(cols)


def test_knowledge_chunk_links_to_document_and_vector() -> None:
    cols = KnowledgeChunk.__table__.columns
    assert "document_pk" in cols
    assert "chunk_index" in cols
    assert "content" in cols
    assert "embedding" in cols
    assert cols["embedding"].type.dim == EMBEDDING_DIMENSIONS
