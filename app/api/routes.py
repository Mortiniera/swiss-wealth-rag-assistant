from fastapi import APIRouter

from app.models.schemas import (
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse
)

from app.rag.ingest import run_ingestion

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):

    try:
        result = run_ingestion(request.source_dir)
        return IngestResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    raise NotImplementedError("Not implemented yet")



