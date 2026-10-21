"""AEGIS AI command-line interface."""
import argparse
from pathlib import Path
import sys

from . import __version__
from .config import Settings
from .orchestrator import run_demo
from .policy import check_target
from .reports.writer import write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aegis", description="AEGIS AI security assessment scaffold")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Show runtime readiness")
    scope = sub.add_parser("scope-check", help="Check whether a target is allowlisted")
    scope.add_argument("target")
    demo = sub.add_parser("demo", help="Run a harmless local demo and write a JSON report")
    demo.add_argument("--target", default="localhost")
    demo.add_argument("--output", default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_env()

    if args.command == "doctor":
        print(f"AEGIS AI {__version__}")
        print("Runtime: ready")
        print("Network scanning: disabled in v0.1")
        print(f"Ollama endpoint configured: {settings.ollama_url}")
        print(f"Ollama model configured: {settings.ollama_model}")
        print(f"Report directory: {settings.report_dir}")
        return

    if args.command == "scope-check":
        decision = check_target(args.target)
        print(("ALLOW: " if decision.allowed else "BLOCK: ") + decision.reason)
        if not decision.allowed:
            raise SystemExit(2)
        return

    if args.command == "demo":
        try:
            report = run_demo(args.target)
        except PermissionError as exc:
            print(f"BLOCKED: {exc}", file=sys.stderr)
            raise SystemExit(2)
        output = args.output or str(Path(settings.report_dir) / f"{report.assessment_id}.json")
        path = write_json(report, output)
        print(f"Demo completed without network access.")
        print(f"Assessment ID: {report.assessment_id}")
        print(f"Report: {path}")
        print(f"Findings: {len(report.findings)} (synthetic demo data)")
        return


if __name__ == "__main__":
    main()
