"""Tests for policy chunking and Postgres ingest (fake embeddings)."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import delete, func, select, text

from app.database.models.knowledge import (
    EMBEDDING_DIMENSIONS,
    KnowledgeChunk,
    KnowledgeDocument,
)
from app.database.session import SessionLocal
from app.rag.policy_ingest import chunk_text, ingest_policies


def _fake_embed(texts: list[str]) -> list[list[float]]:
    return [
        [float((i + 1) % 7) / 7.0] * EMBEDDING_DIMENSIONS for i, _ in enumerate(texts)
    ]


def test_chunk_text_keeps_short_body_as_one_chunk() -> None:
    body = "Short policy body."
    assert chunk_text(body) == [body]


def test_chunk_text_splits_long_body() -> None:
    # Many short sentences so the splitter must pack across chunk_size tokens.
    body = " ".join(f"Policy rule number {i} applies to Helvetia clients." for i in range(80))
    chunks = chunk_text(body, chunk_size=64, overlap=16)
    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_fake_embed_matches_chunk_count_and_dimensions() -> None:
    chunks = chunk_text(
        " ".join(f"Operational detail {i}." for i in range(40)),
        chunk_size=64,
        overlap=16,
    )
    vectors = _fake_embed(chunks)
    assert len(vectors) == len(chunks)
    assert all(len(v) == EMBEDDING_DIMENSIONS for v in vectors)


def _postgres_ready() -> bool:
    try:
        session = SessionLocal()
        try:
            session.execute(text("SELECT 1"))
            session.execute(
                text("SELECT 1 FROM information_schema.tables "
                     "WHERE table_name = 'knowledge_documents'")
            )
            return True
        finally:
            session.close()
    except Exception:
        return False


@pytest.mark.skipif(not _postgres_ready(), reason="Postgres knowledge schema unavailable")
def test_ingest_policies_upserts_into_postgres(tmp_path: Path) -> None:
    (tmp_path / "POL-TEST-001.md").write_text(
        "\n".join(
            [
                "---",
                "document_id: POL-TEST-001",
                "title: Test Policy",
                "department: Compliance",
                "type: policy",
                "category: kyc_refresh",
                "jurisdiction: CH",
                "allowed_roles:",
                "  - relationship_manager",
                "effective_date: 2025-01-01",
                "version: '1.0'",
                "status: active",
                "confidentiality: internal",
                "---",
                "",
                "# Test Policy",
                "",
                "First paragraph about KYC refresh rules for Helvetia Private Bank.",
                "",
                "Second paragraph with more operational detail for retrieval tests.",
            ]
        ),
        encoding="utf-8",
    )

    session = SessionLocal()
    try:
        # Isolate from the real corpus for this test.
        session.execute(delete(KnowledgeChunk))
        session.execute(delete(KnowledgeDocument))
        session.commit()

        result = ingest_policies(
            session, directory=tmp_path, embed_fn=_fake_embed
        )
        assert result["status"] == "success"
        assert result["documents_indexed"] == 1
        assert result["chunks_created"] >= 1

        doc = session.scalars(
            select(KnowledgeDocument).where(
                KnowledgeDocument.document_id == "POL-TEST-001"
            )
        ).one()
        assert doc.title == "Test Policy"
        assert doc.status == "active"
        assert doc.allowed_roles == ["relationship_manager"]

        chunk_count = session.scalar(
            select(func.count())
            .select_from(KnowledgeChunk)
            .where(KnowledgeChunk.document_pk == doc.id)
        )
        assert chunk_count == result["chunks_created"]

        # Idempotent re-run replaces chunks rather than duplicating.
        result2 = ingest_policies(
            session, directory=tmp_path, embed_fn=_fake_embed
        )
        assert result2["documents_indexed"] == 1
        assert result2["chunks_created"] == result["chunks_created"]
        assert (
            session.scalar(select(func.count()).select_from(KnowledgeDocument)) == 1
        )
        assert (
            session.scalar(select(func.count()).select_from(KnowledgeChunk))
            == result["chunks_created"]
        )
    finally:
        session.execute(delete(KnowledgeChunk))
        session.execute(delete(KnowledgeDocument))
        session.commit()
        session.close()
