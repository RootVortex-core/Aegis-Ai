"""Report serialization."""
import json
from pathlib import Path
from ..models import AssessmentReport


def write_json(report: AssessmentReport, output: str | Path) -> Path:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
