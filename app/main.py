from fastapi import FastAPI

import logging
from contextlib import asynccontextmanager

from sqlalchemy import func, select

from app.api.routes import router
from app.api.clients import router as clients_router
from app.api.policies import router as policies_router
from app.api.actors import router as actors_router
from app.config import settings
from app.database.models.knowledge import KnowledgeDocument
from app.database.models.people import Employee
from app.database.seed import seed_database
from app.database.session import SessionLocal
from app.rag.policy_ingest import ingest_policies

from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


def maybe_startup_seed() -> None:
    """Seed synthetic banking data when the domain has no employees.

    Skips when AUTO_SEED is false or employees already exist (Neon persists
    across Render restarts — no reseed on every cold start). Never truncates.
    """
    if not settings.auto_seed:
        logger.info("Startup seed skipped (AUTO_SEED=false)")
        return

    session = SessionLocal()
    try:
        count = session.scalar(select(func.count()).select_from(Employee)) or 0
        if count > 0:
            logger.info(
                "Startup seed skipped (domain already has %d employees)",
                count,
            )
            return
        logger.info(
            "Startup seed: empty domain, loading synthetic clients "
            "(clients=%d, rng_seed=%d)",
            settings.auto_seed_clients,
            settings.seed_rng_seed,
        )
        stats = seed_database(
            session,
            rng_seed=settings.seed_rng_seed,
            client_count=settings.auto_seed_clients,
        )
        logger.info("Startup seed complete: %s", stats)
    except Exception:
        logger.exception(
            "Startup seed failed; API will start without structured demo data"
        )
    finally:
        session.close()


def maybe_startup_ingest() -> None:
    """Load Helvetia policies when the knowledge store is empty.

    Skips when AUTO_INGEST is false, no OpenAI key, or documents already exist
    (Neon persists across Render restarts — no re-embed on every cold start).
    """
    if not settings.auto_ingest:
        logger.info("Startup ingest skipped (AUTO_INGEST=false)")
        return
    if not settings.openai_api_key:
        logger.info("Startup ingest skipped (OPENAI_API_KEY not set)")
        return

    session = SessionLocal()
    try:
        count = session.scalar(select(func.count()).select_from(KnowledgeDocument)) or 0
        if count > 0:
            logger.info(
                "Startup ingest skipped (knowledge store already has %d documents)",
                count,
            )
            return
        logger.info("Startup ingest: knowledge store empty, loading policies")
        result = ingest_policies(session, prune_missing=True)
        logger.info(
            "Startup ingest complete: documents=%d chunks=%d",
            result["documents_indexed"],
            result["chunks_created"],
        )
    except Exception:
        logger.exception("Startup ingest failed; API will start without policy index")
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    maybe_startup_seed()
    maybe_startup_ingest()
    yield


app = FastAPI(
    title="Swiss Wealth RAG Assistant",
    description="Helvetia Private Bank internal operations assistant (policy RAG + structured client APIs)",
    version="0.5.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://swiss-wealth-rag-assistant.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(clients_router)
app.include_router(policies_router)
app.include_router(actors_router)
