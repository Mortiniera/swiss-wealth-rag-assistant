import chromadb
from llama_index.core import Settings as LlamaSettings, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from app.config import settings
from app.rag.common import COLLECTION_NAME, configure_embeddings, get_chroma_client


TOP_K = 3


def _load_index() -> VectorStoreIndex:
    configure_embeddings()

    chroma_client = get_chroma_client()

    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
    except Exception as exc:
        raise ValueError(
            "No indexed documents found. Run POST /ingest first."
        ) from exc

    if collection.count() == 0:
        raise ValueError("Vector store is empty. Run POST /ingest first.")

    vector_store = ChromaVectorStore(chroma_collection=collection)
    return VectorStoreIndex.from_vector_store(vector_store)


def retrieve(question: str, top_k: int = TOP_K) -> list[dict]:
    index = _load_index()
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(question)

    results = []
    for node in nodes:
        results.append({
            "text": node.get_content(),
            "source": node.metadata.get("file_name", "unknown"),
            "chunk_id": node.node_id,
            "score": round(node.score, 4) if node.score is not None else 0.0,
        })

    return results