# AEGIS AI

**Autonomous Ethical Guardian & Intelligence System** — a modular, evidence-first, policy-governed
security assessment platform.

> **Status: v0.2.0 (early development).** This release does not perform network scanning or
> exploitation. The only shipped workflow is a deterministic, offline demo assessment.
> Use AEGIS only on systems you own or are explicitly authorized to assess.

## Design principles

- **Policy before tools:** scope, action, and outbound-endpoint policy are evaluated before any
  assessment step runs; every check fails closed.
- **Evidence first:** a `Finding` cannot be constructed without evidence, and reports that carry no
  evidence are refused at write time.
- **Local/cloud AI:** providers plug in behind one interface; the only shipped adapter is a local
  Ollama adapter that refuses non-loopback endpoints.
- **Safe by default:** no sockets, no scanning, no subprocesses. The demo is deterministic.
- **Auditable:** every report carries timezone-aware ISO-8601 timestamps, the in-scope target, the
  policy decisions that allowed the run, and an explicit `network_access` flag.

## Requirements

- Python 3.11+
- No third-party runtime dependencies

## Quick start

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
aegis doctor
aegis demo
pytest
```

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
aegis doctor
aegis demo
pytest
```

The demo writes a JSON report under `reports/` (git-ignored). It does not contact any remote host.

## CLI

| Command | Purpose | Exit code |
| --- | --- | --- |
| `aegis doctor` | Show runtime readiness, effective allowlist, and endpoint policy | `0` |
| `aegis scope-check <target>` | Evaluate one target against the configured scope | `0` allowed, `2` blocked |
| `aegis demo [--target] [--output]` | Run the offline demo and write a validated JSON report | `0` success, `2` blocked |

`--version` prints the package version. Blocking decisions are always reported on stderr with a
`BLOCKED:` prefix for mutating commands.

## Scope policy

The scope allowlist is a list of hostnames and CIDR networks. Hostnames are matched literally and
are **never** resolved through DNS, so a decision cannot depend on a remote resolver.

| Default entry | Meaning |
| --- | --- |
| `localhost` | Literal loopback hostname |
| `127.0.0.0/8` | Entire IPv4 loopback range |
| `::1/128` | IPv6 loopback address |

Targets are normalized (case, surrounding brackets, a single trailing dot) before matching.
URLs and ranges such as `http://localhost:8000` or `127.0.0.1/8` are rejected as targets rather
than partially interpreted.

### Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `AEGIS_ALLOWED_TARGETS` | `localhost,127.0.0.0/8,::1/128` | Comma-separated hostname/CIDR allowlist. An empty value blocks every target. |
| `AEGIS_REPORT_DIR` | `reports` | Directory for generated reports |
| `AEGIS_OLLAMA_URL` | `http://127.0.0.1:11434` | Optional local model endpoint (loopback only) |
| `AEGIS_OLLAMA_MODEL` | `qwen2.5-coder:3b` | Optional local model name |

## Report format

Reports are written as JSON with `schema_version` `1.1` and validated before they hit disk.

```json
{
  "schema_version": "1.1",
  "assessment_id": "8e640e73-4bbd-4618-b894-19f4008a46ef",
  "created_at": "2026-01-01T12:00:00.000000+00:00",
  "scope": ["localhost"],
  "mode": "demo",
  "findings": [
    {
      "title": "Demo finding: evidence workflow operational",
      "severity": "info",
      "description": "Synthetic finding used to exercise report handling.",
      "evidence": ["source=demo", "network_access=false"],
      "recommendation": "Replace with results from a reviewed, read-only lab adapter.",
      "status": "synthetic"
    }
  ],
  "events": [
    {
      "time": "2026-01-01T12:00:00.000000+00:00",
      "type": "policy_decision",
      "action": "scope-check",
      "allowed": true,
      "reason": "Target is explicitly allowlisted.",
      "network_access": false
    }
  ]
}
```

Validation (`src/aegis/reports/validation.py`) enforces:

- timezone-aware ISO-8601 timestamps on the report and on every event;
- a non-empty scope, at least one finding, and at least one evidence entry per finding;
- supported `mode` and `severity` values;
- at least one **allowed** `policy_decision` event;
- `network_access = false` for every event in `demo` mode.

Invalid reports raise `ReportValidationError` and are never written.

## AI providers

The assessment path does not require a model. `OllamaProvider` is the only shipped adapter and is
never called automatically. Its constructor rejects any endpoint that is not loopback, so a
misconfigured URL cannot send assessment data to a remote host. Model output is advisory and must
never authorize tool execution.

## Development

```bash
python -m pytest      # tests
python -m ruff check .        # lint
python -m ruff format --check .
python -m mypy        # type check (src)
python -m build       # sdist/wheel
```

CI (`.github/workflows/tests.yml`) runs lint, format check, type check, and tests on Python 3.11,
3.12, and 3.13, plus a distribution build on 3.12.

## Project layout

```text
src/aegis/
  cli.py             CLI entry point and exit codes
  config.py          Environment-backed settings
  policy.py          Scope, action, and endpoint policy checks
  models.py          Validated report/finding/audit-event models
  orchestrator.py    Offline demo assessment workflow
  ai/
    base.py          Provider interface
    ollama.py        Loopback-only local Ollama adapter
  reports/
    writer.py        Validated JSON report writer
    validation.py    Persisted report schema validation
tests/
.github/workflows/tests.yml
```

## Safety boundary

This release intentionally does not execute arbitrary shell commands, scan public targets, exploit
vulnerabilities, change system configuration, or transmit assessment data to a cloud model. Those
capabilities require separate reviewed modules, explicit scope authorization, and tests.

## Roadmap

1. ~~Scope policy and immutable audit events.~~ (delivered in 0.2.0)
2. Read-only asset inventory adapters for an isolated lab.
3. ~~Structured findings and evidence validation.~~ (delivered in 0.2.0)
4. Optional local/cloud AI analysis with redaction and user consent.
5. Web/API security checks against an explicitly configured lab.
6. Dashboard, scheduling, and team workflows.

## License

MIT. See `LICENSE`.
