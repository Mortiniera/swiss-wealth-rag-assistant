"""Shared types for knowledge retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class RetrievalFilters:
    """SQL filters applied before vector/FTS ranking."""

    status: str = "active"
    role: Optional[str] = None
    jurisdiction: Optional[str] = None
    category: Optional[str] = None


@dataclass(frozen=True)
class RetrievalHit:
    """One ranked chunk returned by vector, FTS, or hybrid retrieval."""

    chunk_id: UUID
    document_id: str
    document_title: str
    source_file: str
    category: str
    text: str
    score: float
    channel: str  # "vector" | "fts" | "hybrid"
