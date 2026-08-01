"""Read schemas for Helvetia policy catalog."""

from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PolicySummaryOut(BaseModel):
    """Catalog row for the Policies directory (no full body)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: str
    title: str
    department: str
    doc_type: str
    category: str
    jurisdiction: str
    allowed_roles: list[str] = Field(default_factory=list)
    effective_date: date
    version: str
    status: str
    confidentiality: str
    supersedes_document_id: str | None = None
    source_path: str
    updated_at: datetime


class PolicyDetailOut(PolicySummaryOut):
    """Policy detail including markdown body for the workspace reader."""

    body: str
