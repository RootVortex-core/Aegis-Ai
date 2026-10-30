"""Persisted report schema validation.

Reports that fail validation are never written, so downstream consumers can rely
on the shape and on the audit guarantees described in the README.
"""

from __future__ import annotations

from datetime import datetime

from ..models import MODES, SCHEMA_VERSION, SEVERITIES, AssessmentReport


class ReportValidationError(ValueError):
    """Raised when a report does not satisfy the persisted schema."""


def _require_timestamp(value: str, field_name: str) -> None:
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ReportValidationError(f"{field_name} is not an ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise ReportValidationError(f"{field_name} must include timezone information: {value!r}")


def validate_report(report: AssessmentReport) -> None:
    """Validate every persisted invariant, raising ``ReportValidationError``."""
    if report.mode not in MODES:
        raise ReportValidationError(f"Unsupported mode {report.mode!r}.")
    if not report.assessment_id.strip():
        raise ReportValidationError("assessment_id must not be empty.")
    if not report.scope or any(not item.strip() for item in report.scope):
        raise ReportValidationError("scope must contain at least one non-empty target.")

    _require_timestamp(report.created_at, "created_at")

    if not report.findings:
        raise ReportValidationError("at least one finding is required.")
    for index, finding in enumerate(report.findings):
        if finding.severity not in SEVERITIES:
            raise ReportValidationError(f"findings[{index}].severity is unsupported: {finding.severity!r}")
        if not any(item.strip() for item in finding.evidence):
            raise ReportValidationError(f"findings[{index}] must carry at least one evidence entry.")

    if not report.events:
        raise ReportValidationError("at least one audit event is required.")
    for index, event in enumerate(report.events):
        _require_timestamp(event.time, f"events[{index}].time")
        if report.mode == "demo" and event.network_access:
            raise ReportValidationError(f"events[{index}] reports network access, which demo mode forbids.")

    policy_events = [event for event in report.events if event.type == "policy_decision"]
    if not policy_events:
        raise ReportValidationError("at least one policy_decision event is required.")
    if not any(event.allowed for event in policy_events):
        raise ReportValidationError("at least one policy decision must be recorded as allowed.")

    if report.to_dict()["schema_version"] != SCHEMA_VERSION:
        raise ReportValidationError("schema_version does not match the supported version.")
