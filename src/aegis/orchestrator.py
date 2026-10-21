"""Deterministic demo workflow; no network operations are performed."""
from .models import AssessmentReport, Finding
from .policy import check_action, check_target


def run_demo(target: str = "localhost") -> AssessmentReport:
    decision = check_target(target)
    if not decision.allowed:
        raise PermissionError(decision.reason)

    action = check_action("demo")
    if not action.allowed:
        raise PermissionError(action.reason)

    events = [
        {"time": "runtime", "type": "policy_decision", "allowed": True,
         "reason": decision.reason},
        {"time": "runtime", "type": "execution", "action": "demo",
         "network_access": False},
    ]
    findings = [
        Finding(
            title="Demo finding: evidence workflow operational",
            severity="info",
            description="This is a synthetic finding used to demonstrate report handling. It is not a real vulnerability.",
            evidence=["source=demo", "network_access=false"],
            recommendation="Replace this synthetic record with results from a reviewed, read-only lab adapter.",
            status="synthetic",
        )
    ]
    return AssessmentReport.create(scope=[target], mode="demo", findings=findings, events=events)
