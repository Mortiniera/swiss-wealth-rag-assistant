from fastapi import APIRouter, HTTPException
import logging

from app.models.schemas import (
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse,
    RootResponse
)

from app.rag.generator import generate_answer
from app.rag.ingest import run_ingestion

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=RootResponse)
def root():
    return RootResponse(
        name="Swiss Wealth RAG Assistant",
        status="running",
        docs="/docs",
        health="/health",
    )

@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):

    try:
        result = run_ingestion(request.source_dir)

        logger.info(
            "Ingest requested: source_dir=%s documents=%d chunks=%d",
            request.source_dir,
            result["documents_indexed"],
            result["chunks_created"],
        )

        return IngestResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    try:
        logger.info("Question received (length=%d)", len(request.question))
        result = generate_answer(request.question)
        return AskResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


