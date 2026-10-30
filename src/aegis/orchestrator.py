"""Deterministic demo workflow; no network operations are performed."""

from __future__ import annotations

from .models import AssessmentReport, AuditEvent, Finding
from .policy import DEFAULT_ALLOWED_TARGETS, check_action, check_target


def run_demo(
    target: str = "localhost",
    allowed_targets: tuple[str, ...] = DEFAULT_ALLOWED_TARGETS,
) -> AssessmentReport:
    """Run the synthetic, offline assessment and return a validated report.

    Raises ``PermissionError`` when the target or the demo action is blocked by
    policy. The workflow never opens a socket.
    """
    scope_decision = check_target(target, allowed_targets)
    if not scope_decision.allowed:
        raise PermissionError(scope_decision.reason)

    action_decision = check_action("demo")
    if not action_decision.allowed:
        raise PermissionError(action_decision.reason)

    events = [
        AuditEvent(type="policy_decision", action="scope-check", allowed=True, reason=scope_decision.reason),
        AuditEvent(type="policy_decision", action="demo", allowed=True, reason=action_decision.reason),
        AuditEvent(
            type="execution",
            action="demo",
            allowed=True,
            reason="Synthetic findings generated without network access.",
            network_access=False,
        ),
    ]
    findings = [
        Finding(
            title="Demo finding: evidence workflow operational",
            severity="info",
            description=(
                "This is a synthetic finding used to demonstrate report handling. It is not a real vulnerability."
            ),
            evidence=["source=demo", "network_access=false"],
            recommendation="Replace this synthetic record with results from a reviewed, read-only lab adapter.",
            status="synthetic",
        )
    ]
    return AssessmentReport.create(scope=[target], mode="demo", findings=findings, events=events)
