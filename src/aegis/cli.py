"""AEGIS AI command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .config import Settings
from .models import SCHEMA_VERSION
from .orchestrator import run_demo
from .policy import check_action, check_endpoint, check_target
from .reports.writer import write_json

EXIT_OK = 0
EXIT_BLOCKED = 2


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


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()

    action = check_action(args.command)
    if not action.allowed:
        print(f"BLOCKED: {action.reason}", file=sys.stderr)
        return EXIT_BLOCKED

    if args.command == "doctor":
        endpoint = check_endpoint(settings.ollama_url)
        print(f"AEGIS AI {__version__}")
        print(f"Report schema: {SCHEMA_VERSION}")
        print("Runtime: ready")
        print("Network scanning: disabled in this release")
        print(f"Allowed targets: {', '.join(settings.allowed_targets) or '<none>'}")
        print("Permitted actions: demo, doctor, report, scope-check")
        print(f"Ollama endpoint: {settings.ollama_url} ({'allowed' if endpoint.allowed else 'blocked'})")
        print(f"Ollama model: {settings.ollama_model}")
        print(f"Report directory: {settings.report_dir}")
        return EXIT_OK

    if args.command == "scope-check":
        decision = check_target(args.target, settings.allowed_targets)
        print(("ALLOW: " if decision.allowed else "BLOCK: ") + decision.reason)
        return EXIT_OK if decision.allowed else EXIT_BLOCKED

    try:
        report = run_demo(args.target, settings.allowed_targets)
    except PermissionError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return EXIT_BLOCKED

    output = args.output or str(Path(settings.report_dir) / f"{report.assessment_id}.json")
    path = write_json(report, output)
    print("Demo completed without network access.")
    print(f"Assessment ID: {report.assessment_id}")
    print(f"Report: {path}")
    print(f"Findings: {len(report.findings)} (synthetic demo data)")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
