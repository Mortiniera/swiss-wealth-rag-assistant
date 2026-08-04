from pydantic import BaseModel, Field

from typing import Literal


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)


class IngestRequest(BaseModel):
    prune_missing: bool = Field(
        default=True,
        description=(
            "When true, remove knowledge documents that are no longer present "
            "under data/policies/."
        ),
    )


class IngestResponse(BaseModel):
    status: str
    documents_indexed: int
    chunks_created: int
    documents_removed: int = 0


class AskRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to answer",
    )
    history: list[ChatMessage] = Field(
        default_factory=list,
        description="Prior conversation turns (excluding current question)",
    )


class Source(BaseModel):
    institution: str = Field(
        ...,
        description="Policy department (mapped into this legacy field name)",
    )
    document_title: str
    source_file: str
    chunk_id: str
    score: float
    text: str = Field(..., description="Short excerpt from the retrieved chunk")


class EvidenceItem(BaseModel):
    """Structured fact chip from a read-only tool (not a policy citation)."""

    label: str
    value: str
    source: Literal[
        "client_profile",
        "account_summary",
        "account_restrictions",
        "recent_transactions",
        "open_service_requests",
        "interaction_history",
    ] = "client_profile"


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]
    evidence: list[EvidenceItem] = Field(default_factory=list)


class RootResponse(BaseModel):
    name: str
    status: str
    docs: str
    health: str
