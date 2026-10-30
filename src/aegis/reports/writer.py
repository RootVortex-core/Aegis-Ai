"""Report serialization."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import AssessmentReport
from .validation import validate_report


def write_json(report: AssessmentReport, output: str | Path) -> Path:
    """Validate then persist a report, returning the written path."""
    validate_report(report)

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
