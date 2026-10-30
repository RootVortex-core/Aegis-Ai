"""Fail-closed scope, action, and endpoint policy checks.

Every check in this module is offline and deterministic: hostnames are matched
literally and are never resolved through DNS, so a decision cannot depend on a
remote resolver.
"""

from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from urllib.parse import urlsplit

DEFAULT_ALLOWED_TARGETS: tuple[str, ...] = ("localhost", "127.0.0.0/8", "::1/128")

LOOPBACK_NAMES: frozenset[str] = frozenset({"localhost", "localhost.localdomain", "ip6-localhost"})

LOOPBACK_NETWORKS: tuple[ipaddress.IPv4Network | ipaddress.IPv6Network, ...] = (
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
)

SAFE_ACTIONS: frozenset[str] = frozenset({"doctor", "scope-check", "demo", "report"})

ALLOWED_ENDPOINT_SCHEMES: frozenset[str] = frozenset({"http", "https"})


@dataclass(frozen=True)
class PolicyDecision:
    """The outcome of a policy check, with a human-readable reason."""

    allowed: bool
    reason: str


def _normalize_target(target: str) -> str:
    normalized = target.strip().lower()
    if normalized.startswith("[") and normalized.endswith("]"):
        normalized = normalized[1:-1]
    if normalized.endswith("."):
        normalized = normalized[:-1]
    return normalized


def _parse_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value)
    except ValueError:
        return None


def _parse_network(value: str) -> ipaddress.IPv4Network | ipaddress.IPv6Network | None:
    try:
        return ipaddress.ip_network(value, strict=False)
    except ValueError:
        return None


def check_target(
    target: str,
    allowed_targets: tuple[str, ...] = DEFAULT_ALLOWED_TARGETS,
) -> PolicyDecision:
    """Return whether a host or IP falls inside the configured allowlist.

    Allowlist entries are either hostnames or CIDR networks. Targets that look
    like URLs or ranges are rejected instead of being partially interpreted.
    """
    if not target or not target.strip():
        return PolicyDecision(False, "Target is empty; blocked by default.")

    normalized = _normalize_target(target)
    if not normalized:
        return PolicyDecision(False, "Target is empty; blocked by default.")
    if "://" in normalized or "/" in normalized or any(char.isspace() for char in normalized):
        return PolicyDecision(False, "Target must be a single hostname or IP address, not a URL or range.")

    allowed = tuple(entry.strip().lower() for entry in allowed_targets if entry.strip())

    address = _parse_ip(normalized)
    if address is not None:
        for entry in allowed:
            network = _parse_network(entry)
            if network is not None and address.version == network.version and address in network:
                return PolicyDecision(True, f"Target {normalized} is inside allowlisted network {network}.")
        if any(entry == normalized for entry in allowed):
            return PolicyDecision(True, "Target is explicitly allowlisted.")
        return PolicyDecision(False, "Target is not explicitly allowlisted; blocked by default.")

    if any(entry == normalized for entry in allowed):
        return PolicyDecision(True, "Target is explicitly allowlisted.")
    return PolicyDecision(False, "Target is not explicitly allowlisted; blocked by default.")


def check_action(action: str) -> PolicyDecision:
    """Permit only the non-invasive actions shipped in this release."""
    if action in SAFE_ACTIONS:
        return PolicyDecision(True, f"Action '{action}' is permitted.")
    return PolicyDecision(False, f"Action '{action}' is not enabled in this release.")


def check_endpoint(url: str) -> PolicyDecision:
    """Permit outbound HTTP(S) requests only to loopback endpoints."""
    if not url or not url.strip():
        return PolicyDecision(False, "Endpoint is empty; blocked by default.")

    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return PolicyDecision(False, "Endpoint is not a valid URL.")

    if parts.scheme.lower() not in ALLOWED_ENDPOINT_SCHEMES:
        return PolicyDecision(False, "Endpoint scheme must be http or https.")
    host = (parts.hostname or "").lower()
    if not host:
        return PolicyDecision(False, "Endpoint must include a hostname.")

    if host in LOOPBACK_NAMES:
        return PolicyDecision(True, f"Endpoint host {host} is loopback.")

    address = _parse_ip(host)
    if address is not None:
        for network in LOOPBACK_NETWORKS:
            if address.version == network.version and address in network:
                return PolicyDecision(True, f"Endpoint host {address} is loopback.")

    return PolicyDecision(False, "Endpoint host is not loopback; outbound requests are blocked by default.")
