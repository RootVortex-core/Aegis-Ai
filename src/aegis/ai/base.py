"""Provider-neutral interface for future AI analysis."""
from typing import Protocol


class AIProvider(Protocol):
    name: str

    def analyze(self, prompt: str) -> str:
        """Return advisory analysis. Output must never authorize tool execution."""
        ...
