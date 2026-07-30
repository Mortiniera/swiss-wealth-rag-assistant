from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding="utf-8",
        extra='ignore'
    )

    # Optional at startup so read-only API routes can run without LLM usage.
    openai_api_key: str = ""

    documents_dir: Path = Path("data/documents")
    vector_store_dir: Path = Path("vector_store")

    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-5.4-mini"

    auto_ingest_on_startup: bool = True

    database_url: str = (
        "postgresql+psycopg://helvetia:helvetia@localhost:5432/helvetia_bank"
    )
    # Fixed RNG seed for deterministic synthetic data
    seed_rng_seed: int = 42

    @property
    def documents_path(self) -> Path:
        return PROJECT_ROOT / self.documents_dir
    
    @property
    def vector_store_path(self) -> Path: 
        return PROJECT_ROOT / self.vector_store_dir


settings = Settings()