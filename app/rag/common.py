"""Shared LlamaIndex embedding and LLM configuration."""

from llama_index.core import Settings as LlamaSettings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from app.config import settings


def configure_embeddings() -> None:
    """Configure the global OpenAI embedding model used for policy ingest/retrieve."""
    LlamaSettings.embed_model = OpenAIEmbedding(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )


def configure_llm() -> None:
    """Configure the global OpenAI chat model used for intent, rewrite, and answers."""
    LlamaSettings.llm = OpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
    )
