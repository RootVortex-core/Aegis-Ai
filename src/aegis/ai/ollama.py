"""Optional Ollama adapter. It is not called automatically by this release."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen

from ..policy import check_endpoint


class OllamaProvider:
    """Advisory-only adapter for a local Ollama endpoint.

    Construction is refused unless the endpoint is loopback, so a misconfigured
    URL cannot leak assessment data to a remote host.
    """

    name = "ollama"

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5-coder:3b",
        timeout: float = 20.0,
    ) -> None:
        decision = check_endpoint(base_url)
        if not decision.allowed:
            raise PermissionError(decision.reason)

        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def analyze(self, prompt: str) -> str:
        """Return advisory text. The result must never authorize tool execution."""
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout) as response:  # noqa: S310
            result = json.loads(response.read().decode("utf-8"))
        return str(result.get("response", ""))
