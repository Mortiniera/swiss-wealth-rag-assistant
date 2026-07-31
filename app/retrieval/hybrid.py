"""Reciprocal Rank Fusion and hybrid retrieve entrypoint."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.retrieval.fts import search_fts
from app.retrieval.types import RetrievalFilters, RetrievalHit
from app.retrieval.vector import search_vector

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 5
DEFAULT_CANDIDATE_K = 10
RRF_K = 60


def reciprocal_rank_fusion(
    ranked_lists: Sequence[Sequence[RetrievalHit]],
    *,
    rrf_k: int = RRF_K,
    top_k: int = DEFAULT_TOP_K,
) -> list[RetrievalHit]:
    """Merge ranked lists by reciprocal rank (score-scale independent)."""
    scores: dict[str, float] = {}
    payloads: dict[str, RetrievalHit] = {}

    for ranked in ranked_lists:
        for rank, hit in enumerate(ranked, start=1):
            key = str(hit.chunk_id)
            scores[key] = scores.get(key, 0.0) + 1.0 / (rrf_k + rank)
            payloads[key] = hit

    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
    merged: list[RetrievalHit] = []
    for key, score in ordered:
        hit = payloads[key]
        merged.append(
            RetrievalHit(
                chunk_id=hit.chunk_id,
                document_id=hit.document_id,
                document_title=hit.document_title,
                source_file=hit.source_file,
                category=hit.category,
                text=hit.text,
                score=round(score, 6),
                channel="hybrid",
            )
        )
    return merged


def retrieve(
    session: Session,
    query: str,
    *,
    top_k: int = DEFAULT_TOP_K,
    candidate_k: int = DEFAULT_CANDIDATE_K,
    filters: RetrievalFilters | None = None,
    embed_fn=None,
) -> list[RetrievalHit]:
    """Hybrid baseline: vector + FTS candidates merged with RRF."""
    filters = filters or RetrievalFilters()
    vector_hits = search_vector(
        session,
        query,
        top_k=candidate_k,
        filters=filters,
        embed_fn=embed_fn,
    )
    fts_hits = search_fts(
        session,
        query,
        top_k=candidate_k,
        filters=filters,
    )
    results = reciprocal_rank_fusion(
        [vector_hits, fts_hits],
        top_k=top_k,
    )
    if results:
        logger.info(
            "Hybrid retrieve: query=%r hits=%d top=%s/%s score=%.4f",
            query[:80],
            len(results),
            results[0].document_id,
            results[0].document_title,
            results[0].score,
        )
    else:
        logger.info("Hybrid retrieve: query=%r hits=0", query[:80])
    return results
