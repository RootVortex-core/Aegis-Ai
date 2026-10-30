"""Small, serializable domain models with fail-closed validation."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

SCHEMA_VERSION = "1.1"

SEVERITIES: frozenset[str] = frozenset({"info", "low", "medium", "high", "critical"})

FINDING_STATUSES: frozenset[str] = frozenset({"synthetic", "needs_review", "confirmed", "accepted", "false_positive"})

MODES: frozenset[str] = frozenset({"demo"})


def utc_now() -> str:
    """Return the current UTC time as a timezone-aware ISO-8601 string."""
    return datetime.now(UTC).isoformat()


@dataclass
class Finding:
    """A single reportable observation. Findings without evidence are rejected."""

    title: str
    severity: str
    description: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""
    status: str = "needs_review"

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Finding title must not be empty.")
        if not self.description.strip():
            raise ValueError("Finding description must not be empty.")
        if self.severity not in SEVERITIES:
            raise ValueError(f"Unsupported severity {self.severity!r}; expected one of {sorted(SEVERITIES)}.")
        if self.status not in FINDING_STATUSES:
            raise ValueError(f"Unsupported status {self.status!r}; expected one of {sorted(FINDING_STATUSES)}.")
        if not any(item.strip() for item in self.evidence):
            raise ValueError("Findings must carry at least one evidence entry.")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditEvent:
    """A timestamped, append-only record of a policy or execution step."""

    type: str
    action: str
    allowed: bool = True
    reason: str = ""
    network_access: bool = False
    time: str = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.type.strip():
            raise ValueError("Audit event type must not be empty.")
        if not self.action.strip():
            raise ValueError("Audit event action must not be empty.")
        if not self.time.strip():
            raise ValueError("Audit event time must not be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "type": self.type,
            "action": self.action,
            "allowed": self.allowed,
            "reason": self.reason,
            "network_access": self.network_access,
        }


@dataclass
class AssessmentReport:
    """The persisted result of one assessment run."""

    assessment_id: str
    created_at: str
    scope: list[str]
    mode: str
    findings: list[Finding]
    events: list[AuditEvent] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.scope:
            raise ValueError("A report must record at least one in-scope target.")
        if self.mode not in MODES:
            raise ValueError(f"Unsupported mode {self.mode!r}; expected one of {sorted(MODES)}.")
        if not self.findings:
            raise ValueError("A report must contain at least one finding.")

    @classmethod
    def create(
        cls,
        scope: list[str],
        mode: str,
        findings: list[Finding],
        events: list[AuditEvent] | None = None,
    ) -> AssessmentReport:
        return cls(
            assessment_id=str(uuid.uuid4()),
            created_at=utc_now(),
            scope=list(scope),
            mode=mode,
            findings=list(findings),
            events=list(events or []),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "assessment_id": self.assessment_id,
            "created_at": self.created_at,
            "scope": self.scope,
            "mode": self.mode,
            "findings": [item.to_dict() for item in self.findings],
            "events": [item.to_dict() for item in self.events],
        }
