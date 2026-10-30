import json

import pytest

from aegis.ai.ollama import OllamaProvider


def test_remote_provider_endpoint_is_blocked():
    with pytest.raises(PermissionError):
        OllamaProvider(base_url="http://example.com:11434")


def test_analyze_returns_advisory_text(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

        def read(self):
            return json.dumps({"response": "advisory text"}).encode()

    captured = {}

    def fake_urlopen(request, timeout=None):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("aegis.ai.ollama.urlopen", fake_urlopen)

    provider = OllamaProvider()
    assert provider.analyze("hello") == "advisory text"
    assert captured["url"] == "http://127.0.0.1:11434/api/generate"
