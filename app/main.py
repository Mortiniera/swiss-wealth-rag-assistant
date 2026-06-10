from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Swiss Wealth RAG Assistant",
    description="RAG API over public Swiss wealth management content",
    version="0.1.0",
)

app.include_router(router)
