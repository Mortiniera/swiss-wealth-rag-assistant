import chromadb
from llama_index.core import Settings as LlamaSettings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from app.config import settings

COLLECTION_NAME = "swiss_wealth_docs"


def configure_embeddings() -> None:
    LlamaSettings.embed_model = OpenAIEmbedding(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )


def get_chroma_client() -> chromadb.PersistentClient:
    settings.vector_store_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(settings.vector_store_path))

def configure_llm() -> None:
    LlamaSettings.llm = OpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
    )