from fastapi import FastAPI

import logging
from contextlib import asynccontextmanager

from app.api.routes import router
from app.api.clients import router as clients_router

from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Swiss Wealth RAG Assistant",
    description="Helvetia Private Bank internal operations assistant (policy RAG + structured client APIs)",
    version="0.4.0",
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
