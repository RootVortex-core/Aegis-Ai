from aegis.config import Settings
from aegis.policy import DEFAULT_ALLOWED_TARGETS

ENV_VARS = ("AEGIS_OLLAMA_URL", "AEGIS_OLLAMA_MODEL", "AEGIS_REPORT_DIR", "AEGIS_ALLOWED_TARGETS")


def test_defaults(monkeypatch):
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)

    settings = Settings.from_env()

    assert settings.allowed_targets == DEFAULT_ALLOWED_TARGETS
    assert settings.report_dir == "reports"
    assert settings.ollama_url == "http://127.0.0.1:11434"


def test_environment_overrides(monkeypatch):
    monkeypatch.setenv("AEGIS_ALLOWED_TARGETS", "10.0.0.0/8, lab.local")
    monkeypatch.setenv("AEGIS_REPORT_DIR", "/tmp/aegis-reports")

    settings = Settings.from_env()

    assert settings.allowed_targets == ("10.0.0.0/8", "lab.local")
    assert settings.report_dir == "/tmp/aegis-reports"


def test_empty_allowlist_override_blocks_everything(monkeypatch):
    monkeypatch.setenv("AEGIS_ALLOWED_TARGETS", "")

    settings = Settings.from_env()

    assert settings.allowed_targets == ()
