"""pgvector nearest-neighbor search over knowledge chunks."""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from llama_index.core import Settings as LlamaSettings
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.knowledge import KnowledgeChunk, KnowledgeDocument
from app.rag.common import configure_embeddings
from app.retrieval.filters import document_filter_clause
from app.retrieval.types import RetrievalFilters, RetrievalHit

EmbedFn = Callable[[list[str]], list[list[float]]]


def _embed_query(query: str, embed_fn: EmbedFn | None) -> list[float]:
    """Embed the user query; use ``embed_fn`` when provided (tests), else OpenAI."""
    if embed_fn is not None:
        vectors = embed_fn([query])
        if not vectors:
            raise ValueError("embed_fn returned no vectors")
        return vectors[0]

    configure_embeddings()
    model = LlamaSettings.embed_model
    if model is None:
        raise RuntimeError("Embedding model is not configured")
    return model.get_query_embedding(query)


def search_vector(
    session: Session,
    query: str,
    *,
    top_k: int = 10,
    filters: RetrievalFilters | None = None,
    embed_fn: EmbedFn | None = None,
) -> list[RetrievalHit]:
    """Return top-k chunks by cosine distance to the query embedding."""
    filters = filters or RetrievalFilters()
    query = query.strip()
    if not query or top_k <= 0:
        return []

    embedding = _embed_query(query, embed_fn)
    distance = KnowledgeChunk.embedding.cosine_distance(embedding)
    similarity = (1 - distance).label("score")

    stmt = (
        select(
            KnowledgeChunk.id,
            KnowledgeChunk.content,
            KnowledgeDocument.document_id,
            KnowledgeDocument.title,
            KnowledgeDocument.department,
            KnowledgeDocument.source_path,
            KnowledgeDocument.category,
            similarity,
        )
        .join(
            KnowledgeDocument,
            KnowledgeDocument.id == KnowledgeChunk.document_pk,
        )
        .where(
            document_filter_clause(filters),
            KnowledgeChunk.embedding.is_not(None),
        )
        .order_by(distance)
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
                channel="vector",
            )
        )
    return hits
