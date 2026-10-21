# AEGIS AI

**Autonomous Ethical Guardian & Intelligence System** — a modular, evidence-first security assessment platform.

> Early development scaffold. This release does not perform network scanning or exploitation.
> Use AEGIS only on systems you own or are explicitly authorized to assess.

## Design principles

- **Policy before tools:** scope and action policy are checked before an assessment step.
- **Evidence first:** findings must carry evidence; model output is advisory, never authoritative.
- **Local/cloud AI:** model providers plug in behind one interface; no provider is required in v0.1.
- **Safe by default:** the first release runs a local demo assessment only.
- **Auditable:** reports include timestamps, scope, findings, and policy decisions.

## Requirements

- Python 3.11+
- No third-party runtime dependencies for the initial demo

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

The demo writes a JSON report under `reports/`. It does not contact any remote host.

## CLI

- `aegis doctor` — show runtime readiness.
- `aegis scope-check <target>` — evaluate a target against the configured scope.
- `aegis demo` — run a harmless, deterministic demonstration and write a report.

## Project layout

```text
src/aegis/
  cli.py             CLI entry point
  config.py          Environment-backed settings
  policy.py          Scope and action policy checks
  models.py          Typed report/finding models
  orchestrator.py    Assessment workflow
  ai/
    base.py          Provider interface
    ollama.py        Optional local Ollama adapter
  reports/
    writer.py        JSON report writer
tests/
.github/workflows/tests.yml
```

## AI configuration

The initial assessment does not require an AI provider. For optional local model connectivity:

```bash
export AEGIS_OLLAMA_URL=http://127.0.0.1:11434
export AEGIS_OLLAMA_MODEL=qwen2.5-coder:3b
```

`aegis doctor` checks only whether the local endpoint is configured; the starter does not send data to a model automatically. Cloud providers should be added only through the same provider interface, with explicit data-sharing controls.

## Safety boundary

The first version intentionally does not execute arbitrary shell commands, scan public targets, exploit vulnerabilities, change system configuration, or transmit assessment data to a cloud model. These capabilities require separate reviewed modules, explicit scope authorization, and tests.

## Roadmap

1. Scope policy and immutable audit events.
2. Read-only asset inventory adapters for an isolated lab.
3. Structured findings and evidence validation.
4. Optional local/cloud AI analysis with redaction and user consent.
5. Web/API security checks against an explicitly configured lab.
6. Dashboard, scheduling, and team workflows.

## License

MIT. See `LICENSE`.
