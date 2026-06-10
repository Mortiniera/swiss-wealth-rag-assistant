from fastapi import FastAPI

import logging
from contextlib import asynccontextmanager

from app.api.routes import router
from app.rag.ingest import ensure_index

from app.config import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.auto_ingest_on_startup:
        result = ensure_index(str(settings.documents_dir))
        if result:
            logger.info("Startup ingest: %s", result)
        else:
            logger.info("Startup ingest skipped (index already exists)")
    yield

app = FastAPI(
    title="Swiss Wealth RAG Assistant",
    description="RAG API over public Swiss wealth management content",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(router)
