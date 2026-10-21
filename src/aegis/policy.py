"""Fail-closed scope and action policy checks."""
from dataclasses import dataclass
import ipaddress


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


def check_target(target: str, allowed_targets: tuple[str, ...] = ("localhost", "127.0.0.1", "::1")) -> PolicyDecision:
    """Only allow exact, explicitly listed targets in this starter release."""
    normalized = target.strip().lower()
    allowed = {item.lower() for item in allowed_targets}
    if normalized in allowed:
        return PolicyDecision(True, "Target is explicitly allowlisted.")
    return PolicyDecision(False, "Target is not explicitly allowlisted; blocked by default.")


def check_action(action: str) -> PolicyDecision:
    """The starter only supports non-invasive demo/report actions."""
    safe_actions = {"demo", "report", "doctor", "scope-check"}
    if action in safe_actions:
        return PolicyDecision(True, f"Action '{action}' is permitted.")
    return PolicyDecision(False, f"Action '{action}' is not enabled in this release.")
