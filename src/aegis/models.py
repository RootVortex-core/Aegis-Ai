"""Small, serializable domain models."""
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Finding:
    title: str
    severity: str
    description: str
    evidence: list[str] = field(default_factory=list)
    recommendation: str = ""
    status: str = "needs_review"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AssessmentReport:
    assessment_id: str
    created_at: str
    scope: list[str]
    mode: str
    findings: list[Finding]
    events: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def create(cls, scope: list[str], mode: str, findings: list[Finding],
               events: list[dict[str, Any]] | None = None) -> "AssessmentReport":
        return cls(
            assessment_id=str(uuid.uuid4()),
            created_at=utc_now(),
            scope=scope,
            mode=mode,
            findings=findings,
            events=events or [],
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "assessment_id": self.assessment_id,
            "created_at": self.created_at,
            "scope": self.scope,
            "mode": self.mode,
            "findings": [item.to_dict() for item in self.findings],
            "events": self.events,
        }
