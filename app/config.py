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

    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-5.4-mini"

    database_url: str = (
        "postgresql+psycopg://helvetia:helvetia@localhost:5432/helvetia_bank"
    )
    # Fixed RNG seed for deterministic synthetic data
    seed_rng_seed: int = 42

    # If true, empty knowledge tables are filled from data/policies/ on API startup.
    auto_ingest: bool = True

    # If true, empty banking domain (no employees) is seeded on API startup.
    # Neon-safe: skips when employees already exist. Never truncates.
    auto_seed: bool = True
    auto_seed_clients: int = 500


settings = Settings()
