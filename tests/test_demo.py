import json
from aegis.orchestrator import run_demo
from aegis.reports.writer import write_json
import pytest


def test_demo_creates_synthetic_finding(tmp_path):
    report = run_demo()
    output = write_json(report, tmp_path / "report.json")
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["mode"] == "demo"
    assert data["findings"][0]["status"] == "synthetic"
    assert data["events"][1]["network_access"] is False


def test_demo_rejects_non_allowlisted_target():
    with pytest.raises(PermissionError):
        run_demo("example.com")
