"""Tests for hybrid retrieval (RRF + optional Postgres integration)."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import func, select, text

from app.database.models.knowledge import KnowledgeDocument
from app.database.session import SessionLocal
from app.retrieval.hybrid import reciprocal_rank_fusion, retrieve
from app.retrieval.types import RetrievalFilters, RetrievalHit


def _hit(doc_id: str, chunk_key: str, score: float, channel: str) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=uuid4(),
        document_id=doc_id,
        document_title=doc_id,
        source_file=f"{doc_id}.md",
        category="test",
        text=f"body {chunk_key}",
        score=score,
        channel=channel,
    )


def test_reciprocal_rank_fusion_prefers_items_in_both_lists() -> None:
    shared = _hit("POL-BOTH", "shared", 0.9, "vector")
    only_vector = _hit("POL-VEC", "vec", 0.8, "vector")
    only_fts = _hit("POL-FTS", "fts", 0.8, "fts")

    # Same chunk must share chunk_id across lists for RRF to fuse.
    shared_fts = RetrievalHit(
        chunk_id=shared.chunk_id,
        document_id=shared.document_id,
        document_title=shared.document_title,
        source_file=shared.source_file,
        category=shared.category,
        text=shared.text,
        score=0.7,
        channel="fts",
    )

    merged = reciprocal_rank_fusion(
        [[shared, only_vector], [shared_fts, only_fts]],
        top_k=3,
    )
    assert merged[0].chunk_id == shared.chunk_id
    assert merged[0].channel == "hybrid"
    assert {h.document_id for h in merged} == {"POL-BOTH", "POL-VEC", "POL-FTS"}


def test_reciprocal_rank_fusion_empty() -> None:
    assert reciprocal_rank_fusion([[], []]) == []


def _postgres_knowledge_ready() -> bool:
    try:
        session = SessionLocal()
        try:
            session.execute(text("SELECT 1"))
            count = session.scalar(select(func.count()).select_from(KnowledgeDocument))
            return bool(count and count > 0)
        finally:
            session.close()
    except Exception:
        return False


@pytest.mark.skipif(
    not _postgres_knowledge_ready(),
    reason="Postgres knowledge corpus not available",
)
def test_fts_active_kyc_beats_superseded() -> None:
    from app.retrieval.fts import search_fts

    session = SessionLocal()
    try:
        hits = search_fts(
            session,
            "KYC refresh interval expired documents",
            top_k=5,
            filters=RetrievalFilters(status="active"),
        )
        assert hits, "expected FTS hits for KYC query"
        assert hits[0].document_id == "POL-KYC-002"
        assert all(h.document_id != "POL-KYC-001" for h in hits)
    finally:
        session.close()


@pytest.mark.skipif(
    not _postgres_knowledge_ready(),
    reason="Postgres knowledge corpus not available",
)
def test_hybrid_retrieve_with_fake_embeddings_still_returns_fts_signal() -> None:
    """Vector branch uses fake embeds; FTS alone should still surface KYC."""
    from app.database.models.knowledge import EMBEDDING_DIMENSIONS

    session = SessionLocal()

    def fake_embed(texts: list[str]) -> list[list[float]]:
        return [[0.01] * EMBEDDING_DIMENSIONS for _ in texts]

    try:
        hits = retrieve(
            session,
            "KYC refresh policy for expired identity documents",
            top_k=5,
            filters=RetrievalFilters(status="active"),
            embed_fn=fake_embed,
        )
        assert hits
        doc_ids = [h.document_id for h in hits]
        assert "POL-KYC-002" in doc_ids
        assert "POL-KYC-001" not in doc_ids
    finally:
        session.close()
