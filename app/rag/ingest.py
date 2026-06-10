from pathlib import Path


from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore


from app.config import PROJECT_ROOT
from app.rag.common import COLLECTION_NAME, configure_embeddings, get_chroma_client

def run_ingestion(source_dir: str) -> dict:

    source_path = (PROJECT_ROOT / source_dir).resolve()
    if not source_path.exists() :
        raise FileNotFoundError(f"Source directory not found: {source_path}")


    # Loads files from the folder
    documents = SimpleDirectoryReader(str(source_path)).load_data()
    if not documents: 
        raise ValueError(f"No documents found in {source_path}")


    configure_embeddings()

    chroma_client=get_chroma_client()

    # Replaces the index instead of duplicating
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    
    collection = chroma_client.create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )

    return {
        "status" : "success",
        "documents_indexed" : len(documents),
        "chunks_created" : collection.count()
    }


def is_index_ready() -> bool:
    chroma_client = get_chroma_client()
    try:
        collection = chroma_client.get_collection(COLLECTION_NAME)
        return collection.count() > 0
    except Exception:
        return False

def ensure_index(source_dir: str = "data/documents") -> dict | None:
    if is_index_ready():
        return None
    return run_ingestion(source_dir)

