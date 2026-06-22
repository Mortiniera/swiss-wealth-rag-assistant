from pydantic import BaseModel, Field

from typing import Literal


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)

class IngestRequest(BaseModel):
    source_dir: str = Field(
        default="data/documents",
        description="Directory containing documents to index"
    )


class IngestResponse(BaseModel):
    status: str
    documents_indexed: int
    chunks_created: int



class AskRequest(BaseModel):
    question:str = Field(
        ...,
        min_length=1, 
        description="Question to answer"
    )
    history: list[ChatMessage] = Field(
        default_factory=list,
        description="Prior conversation turns (excluding current question)"
    )


class Source(BaseModel):
    institution: str
    document_title: str
    source_file: str
    chunk_id: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


class RootResponse(BaseModel):
    name: str
    status: str
    docs: str
    health: str