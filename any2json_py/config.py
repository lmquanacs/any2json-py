from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    coordinator_model: str = "openai/gpt-4o"
    worker_model: str = "openai/gpt-4o-mini"
    max_file_size_mb: int = 50
    context_threshold_tokens: int = 100_000
    chunk_size_tokens: int = 8_000
    chunk_overlap_tokens: int = 200


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
