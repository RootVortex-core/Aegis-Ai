import json
from datetime import datetime

import pytest

from aegis.models import SCHEMA_VERSION, AssessmentReport, AuditEvent, Finding
from aegis.orchestrator import run_demo
from aegis.reports.validation import ReportValidationError, validate_report
from aegis.reports.writer import write_json


def test_demo_creates_valid_synthetic_finding(tmp_path):
    report = run_demo()
    output = write_json(report, tmp_path / "report.json")
    data = json.loads(output.read_text(encoding="utf-8"))

    assert data["schema_version"] == SCHEMA_VERSION
    assert data["mode"] == "demo"
    assert data["findings"][0]["status"] == "synthetic"
    assert data["findings"][0]["evidence"]
    assert data["events"][0]["type"] == "policy_decision"
    assert all(event["network_access"] is False for event in data["events"])


def test_demo_records_timezone_aware_timestamps():
    report = run_demo()
    values = [report.created_at, *(event.time for event in report.events)]

    assert len(values) == 4
    for value in values:
        assert datetime.fromisoformat(value).tzinfo is not None


def test_demo_rejects_non_allowlisted_target():
    with pytest.raises(PermissionError):
        run_demo("example.com")


def test_demo_honours_configured_allowlist():
    report = run_demo("10.20.30.40", allowed_targets=("10.0.0.0/8",))

    assert report.scope == ["10.20.30.40"]


def test_finding_requires_evidence():
    with pytest.raises(ValueError):
        Finding(title="Missing evidence", severity="info", description="No evidence attached.")


def test_finding_rejects_unknown_severity():
    with pytest.raises(ValueError):
        Finding(title="Bad severity", severity="urgent", description="Unknown level.", evidence=["source=test"])


def test_validation_rejects_network_access_in_demo_mode():
    finding = Finding(title="Synthetic", severity="info", description="Synthetic.", evidence=["source=test"])
    report = AssessmentReport.create(
        scope=["localhost"],
        mode="demo",
        findings=[finding],
        events=[
            AuditEvent(type="policy_decision", action="scope-check", allowed=True),
            AuditEvent(type="execution", action="demo", network_access=True),
        ],
    )

    with pytest.raises(ReportValidationError):
        validate_report(report)


def test_validation_requires_policy_decision():
    finding = Finding(title="Synthetic", severity="info", description="Synthetic.", evidence=["source=test"])
    report = AssessmentReport.create(
        scope=["localhost"],
        mode="demo",
        findings=[finding],
        events=[AuditEvent(type="execution", action="demo")],
    )

    with pytest.raises(ReportValidationError):
        validate_report(report)


def test_writer_refuses_invalid_report(tmp_path):
    finding = Finding(title="Synthetic", severity="info", description="Synthetic.", evidence=["source=test"])
    report = AssessmentReport.create(scope=["localhost"], mode="demo", findings=[finding], events=[])

    with pytest.raises(ReportValidationError):
        write_json(report, tmp_path / "report.json")
    assert not (tmp_path / "report.json").exists()
