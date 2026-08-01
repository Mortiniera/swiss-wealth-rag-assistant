"""PostgreSQL full-text search over knowledge chunks."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, literal_column, select
from sqlalchemy.orm import Session

from app.database.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.retrieval.filters import document_filter_clause
from app.retrieval.types import RetrievalFilters, RetrievalHit


def search_fts(
    session: Session,
    query: str,
    *,
    top_k: int = 10,
    filters: RetrievalFilters | None = None,
) -> list[RetrievalHit]:
    """Return top-k chunks by Postgres FTS rank (english config)."""
    filters = filters or RetrievalFilters()
    query = query.strip()
    if not query or top_k <= 0:
        return []

    ts_query = func.plainto_tsquery("english", query)

    # Prefer generated content_tsv (Alembic 0003); fall back to inline to_tsvector.
    tsv = literal_column("knowledge_chunks.content_tsv")
    rank = func.ts_rank_cd(tsv, ts_query).label("score")
    stmt = (
        select(
            KnowledgeChunk.id,
            KnowledgeChunk.content,
            KnowledgeDocument.document_id,
            KnowledgeDocument.title,
            KnowledgeDocument.department,
            KnowledgeDocument.source_path,
            KnowledgeDocument.category,
            rank,
        )
        .join(
            KnowledgeDocument,
            KnowledgeDocument.id == KnowledgeChunk.document_pk,
        )
        .where(
            document_filter_clause(filters),
            tsv.op("@@")(ts_query),
        )
        .order_by(rank.desc())
        .limit(top_k)
    )

    try:
        rows = session.execute(stmt).all()
    except Exception:
        session.rollback()
        inline_tsv = func.to_tsvector("english", KnowledgeChunk.content)
        rank = func.ts_rank_cd(inline_tsv, ts_query).label("score")
        stmt = (
            select(
                KnowledgeChunk.id,
                KnowledgeChunk.content,
                KnowledgeDocument.document_id,
                KnowledgeDocument.title,
                KnowledgeDocument.department,
                KnowledgeDocument.source_path,
                KnowledgeDocument.category,
                rank,
            )
            .join(
                KnowledgeDocument,
                KnowledgeDocument.id == KnowledgeChunk.document_pk,
            )
            .where(
                document_filter_clause(filters),
                inline_tsv.op("@@")(ts_query),
            )
            .order_by(rank.desc())
            .limit(top_k)
        )
        rows = session.execute(stmt).all()

    hits: list[RetrievalHit] = []
    for row in rows:
        hits.append(
            RetrievalHit(
                chunk_id=row.id if isinstance(row.id, UUID) else UUID(str(row.id)),
                document_id=row.document_id,
                document_title=row.title,
                department=row.department,
                source_file=row.source_path,
                category=row.category,
                text=row.content,
                score=round(float(row.score), 6),
                channel="fts",
            )
        )
    return hits
