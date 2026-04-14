from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import yaml


_CONFIG_PATH = Path(__file__).parent.parent / "config.yml"


@dataclass
class ModelConfig:
    text: str = "openai/gpt-4o-mini"
    image: str = "openai/gpt-4o"
    worker: str = "openai/gpt-4o-mini"
    coordinator: str = "openai/gpt-4o"


@dataclass
class Settings:
    models: ModelConfig
    max_file_size_mb: int = 50
    context_threshold_tokens: int = 100_000
    chunk_size_tokens: int = 8_000
    chunk_overlap_tokens: int = 200


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    if _CONFIG_PATH.exists():
        raw = yaml.safe_load(_CONFIG_PATH.read_text())
        models = ModelConfig(**raw.get("models", {}))
        limits = raw.get("limits", {})
    else:
        models = ModelConfig()
        limits = {}
    return Settings(
        models=models,
        max_file_size_mb=limits.get("max_file_size_mb", 50),
        context_threshold_tokens=limits.get("context_threshold_tokens", 100_000),
        chunk_size_tokens=limits.get("chunk_size_tokens", 8_000),
        chunk_overlap_tokens=limits.get("chunk_overlap_tokens", 200),
    )
