from fastapi import APIRouter

from app.models.schemas import (
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse
)

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):
    raise NotImplementedError("Not implemented yet")

@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    raise NotImplementedError("Not implemented yet")



