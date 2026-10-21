"""Runtime configuration for AEGIS AI."""
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen2.5-coder:3b"
    report_dir: str = "reports"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            ollama_url=os.getenv("AEGIS_OLLAMA_URL", cls.ollama_url),
            ollama_model=os.getenv("AEGIS_OLLAMA_MODEL", cls.ollama_model),
            report_dir=os.getenv("AEGIS_REPORT_DIR", cls.report_dir),
        )
