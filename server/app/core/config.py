import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[3] / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # LLM Provider Configuration
    LLM_PROVIDER: str = "google"

    # Provider Keys
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_LLM_MODEL: str = "google/gemma-4-31b-it"
    OPENROUTER_EMBEDDING_MODEL: str = "nvidia/nemotron-3-embed-1b"
    OPENROUTER_MODEL: str = "nvidia/nemotron-3-embed-1b"

    NVIDIA_API_KEY: str | None = None
    NVIDIA_MODEL: str = "google/gemma-4-27b-it"

    GOOGLE_API_KEY: str | None = None
    GOOGLE_MODEL: str = "gemma-4-27b-it"
    GEMMA_MODEL: str = "gemma-4-27b-it"

    # Database Configuration
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Graph Retrieval & Reasoning Weights / Parameters
    VECTOR_TOP_K: int = 20
    STRUCTURED_TOP_K: int = 20
    RELATIONSHIP_TOP_K: int = 10
    FINAL_EVIDENCE_COUNT: int = 10

    VECTOR_WEIGHT: float = 0.55
    VARIABLE_WEIGHT: float = 0.20
    INTERVENTION_WEIGHT: float = 0.10
    CONTEXT_WEIGHT: float = 0.10
    EVIDENCE_WEIGHT: float = 0.05

settings = Settings()
