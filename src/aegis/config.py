"""Runtime configuration for AEGIS AI."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .policy import DEFAULT_ALLOWED_TARGETS

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:3b"
DEFAULT_REPORT_DIR = "reports"


@dataclass(frozen=True)
class Settings:
    """Immutable settings resolved once from the environment."""

    ollama_url: str = DEFAULT_OLLAMA_URL
    ollama_model: str = DEFAULT_OLLAMA_MODEL
    report_dir: str = DEFAULT_REPORT_DIR
    allowed_targets: tuple[str, ...] = DEFAULT_ALLOWED_TARGETS

    @classmethod
    def from_env(cls) -> Settings:
        raw_targets = os.getenv("AEGIS_ALLOWED_TARGETS")
        if raw_targets is None:
            allowed_targets = DEFAULT_ALLOWED_TARGETS
        else:
            allowed_targets = tuple(item.strip() for item in raw_targets.split(",") if item.strip())

        return cls(
            ollama_url=os.getenv("AEGIS_OLLAMA_URL", DEFAULT_OLLAMA_URL),
            ollama_model=os.getenv("AEGIS_OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
            report_dir=os.getenv("AEGIS_REPORT_DIR", DEFAULT_REPORT_DIR),
            allowed_targets=allowed_targets,
        )
