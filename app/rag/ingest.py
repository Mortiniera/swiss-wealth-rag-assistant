from pathlib import Path

import chromadb
from llama_index.core import Settings as LlamaSettings
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore


from app.config import PROJECT_ROOT, settings

COLLECTION_NAME = "swiss_wealth_docs"

def run_ingestion(source_dir: str) -> dict:

    source_path = (PROJECT_ROOT / source_dir).resolve()
    if not source_path.exists() :
        raise FileNotFoundError(f"Source directory not found: {source_path}")


    # Loads files from the folder
    documents = SimpleDirectoryReader(str(source_path)).load_data()
    if not documents: 
        raise ValueError(f"No documents found in {source_path}")


    # Embeds chunks
    LlamaSettings.embed_model = OpenAIEmbedding(
        model=settings.embedding_model,
        api_key=settings.openai_api_key
    )


    # Persists vectors under vector_store/
    settings.vector_store_path.mkdir(parents=True, exist_ok=True)

    chroma_client=chromadb.PersistentClient(path=str(settings.vector_store_path))

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

