from pydantic import BaseModel, Field


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