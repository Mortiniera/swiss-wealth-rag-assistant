"""Ingest Helvetia policy Markdown into Postgres + pgvector."""

from __future__ import annotations

import logging
import uuid
from collections.abc import Callable
from pathlib import Path

from llama_index.core import Settings as LlamaSettings
from llama_index.core.node_parser import SentenceSplitter
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import PROJECT_ROOT
from app.database.models.knowledge import (
    EMBEDDING_DIMENSIONS,
    KnowledgeChunk,
    KnowledgeDocument,
)
from app.rag.common import configure_embeddings
from app.rag.policy_registry import PolicyDocument, load_policies, policies_dir

logger = logging.getLogger(__name__)

# SentenceSplitter sizes are in *tokens* (approx.), not characters.
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

EmbedFn = Callable[[list[str]], list[list[float]]]


def chunk_text(
    text: str,
    *,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Split policy body with LlamaIndex SentenceSplitter.

    Behaviour : split into sentences -> pack into chunks up to
    ``chunk_size`` tokens -> overlap consecutive chunks by ``overlap`` tokens.
    ``paragraph_separator`` prefers Markdown paragraph breaks before falling
    back to sentence/regex splits for oversized units.
    """
    cleaned = text.strip()
    if not cleaned:
        return []

    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        paragraph_separator="\n\n",
    )
    return [piece.strip() for piece in splitter.split_text(cleaned) if piece.strip()]


def default_embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts with the configured OpenAI embedding model."""
    if not texts:
        return []
    configure_embeddings()
    model = LlamaSettings.embed_model
    if model is None:
        raise RuntimeError("Embedding model is not configured")
    vectors = model.get_text_embedding_batch(texts)
    for vector in vectors:
        if len(vector) != EMBEDDING_DIMENSIONS:
            raise ValueError(
                f"Expected embedding dim {EMBEDDING_DIMENSIONS}, got {len(vector)}"
            )
    return vectors


def _relative_source_path(path: Path) -> str:
    """Return path relative to project root when possible (for stored source_path)."""
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _apply_document_fields(row: KnowledgeDocument, policy: PolicyDocument) -> None:
    """Copy policy registry metadata onto a KnowledgeDocument ORM row."""
    row.title = policy.title
    row.department = policy.department
    row.doc_type = policy.type
    row.category = policy.category
    row.jurisdiction = policy.jurisdiction
    row.allowed_roles = list(policy.allowed_roles)
    row.effective_date = policy.effective_date
    row.version = policy.version
    row.status = policy.status
    row.confidentiality = policy.confidentiality
    row.supersedes_document_id = policy.supersedes
    row.source_path = _relative_source_path(policy.source_path)
    row.body = policy.body


def ingest_policies(
    session: Session,
    *,
    directory: Path | None = None,
    embed_fn: EmbedFn | None = None,
    prune_missing: bool = True,
) -> dict:
    """Load policy files and upsert documents + embedded chunks.

    Re-runs replace chunks for each document_id. When ``prune_missing`` is true,
    documents present in the DB but missing from disk are removed.
    """
    policies = load_policies(directory or policies_dir())
    embed = embed_fn or default_embed_texts

    existing_rows = {
        row.document_id: row
        for row in session.scalars(select(KnowledgeDocument)).all()
    }
    seen_ids: set[str] = set()
    total_chunks = 0

    for policy in policies:
        seen_ids.add(policy.document_id)
        row = existing_rows.get(policy.document_id)
        if row is None:
            row = KnowledgeDocument(id=uuid.uuid4(), document_id=policy.document_id)
            session.add(row)
            existing_rows[policy.document_id] = row

        _apply_document_fields(row, policy)
        session.flush()

        session.execute(
            delete(KnowledgeChunk).where(KnowledgeChunk.document_pk == row.id)
        )

        pieces = chunk_text(policy.body)
        if not pieces:
            raise ValueError(f"{policy.document_id}: no chunks produced from body")

        vectors = embed(pieces)
        if len(vectors) != len(pieces):
            raise ValueError(
                f"{policy.document_id}: embed_fn returned {len(vectors)} vectors "
                f"for {len(pieces)} chunks"
            )

        for index, (content, vector) in enumerate(zip(pieces, vectors, strict=True)):
            session.add(
                KnowledgeChunk(
                    id=uuid.uuid4(),
                    document_pk=row.id,
                    chunk_index=index,
                    content=content,
                    embedding=vector,
                )
            )
        total_chunks += len(pieces)

    removed = 0
    if prune_missing:
        stale_ids = [doc_id for doc_id in existing_rows if doc_id not in seen_ids]
        if stale_ids:
            session.execute(
                delete(KnowledgeDocument).where(
                    KnowledgeDocument.document_id.in_(stale_ids)
                )
            )
            removed = len(stale_ids)

    session.commit()

    result = {
        "status": "success",
        "documents_indexed": len(seen_ids),
        "chunks_created": total_chunks,
        "documents_removed": removed,
    }
    logger.info(
        "Policy ingest complete: documents=%d chunks=%d removed=%d",
        result["documents_indexed"],
        result["chunks_created"],
        result["documents_removed"],
    )
    return result
