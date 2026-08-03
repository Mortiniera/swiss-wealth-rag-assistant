from app.agent.orchestrator import handle_question
from app.config import settings
from app.database.session import SessionLocal
from app.api.deps import get_optional_actor
from app.database.models.people import Employee
from app.models.schemas import (
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse,
    RootResponse,
)
from app.rag.policy_ingest import ingest_policies

from fastapi import APIRouter, Depends, HTTPException
import logging

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
    """Ingest Helvetia policies from data/policies into Postgres + pgvector."""
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY is required for policy embeddings.",
        )

    session = SessionLocal()
    try:
        result = ingest_policies(session, prune_missing=request.prune_missing)
        logger.info(
            "Policy ingest requested: documents=%d chunks=%d removed=%d",
            result["documents_indexed"],
            result["chunks_created"],
            result["documents_removed"],
        )
        return IngestResponse(**result)
    except FileNotFoundError as e:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(e)) from e
    except ValueError as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        session.rollback()
        logger.exception("Policy ingest failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
    finally:
        session.close()


@router.post("/ask", response_model=AskResponse)
def ask(
    request: AskRequest,
    actor: Employee | None = Depends(get_optional_actor),
):
    try:
        logger.info(
            "Question received (length=%d, history_turns=%d, actor=%s)",
            len(request.question),
            len(request.history),
            actor.employee_code if actor else None,
        )
        role = actor.role.code if actor is not None else None
        actor_code = actor.employee_code if actor is not None else None
        result = handle_question(
            request.question,
            request.history,
            role=role,
            actor_employee_code=actor_code,
        )
        return AskResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
