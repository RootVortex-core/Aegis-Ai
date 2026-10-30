import pytest

from aegis.policy import check_action, check_endpoint, check_target


@pytest.mark.parametrize(
    "target",
    ["localhost", "LOCALHOST", "localhost.", "127.0.0.1", "127.0.0.5", "::1", "[::1]"],
)
def test_loopback_targets_are_allowlisted(target):
    assert check_target(target).allowed


@pytest.mark.parametrize(
    "target",
    [
        "example.com",
        "localhost.example.com",
        "10.0.0.1",
        "0.0.0.0",
        "http://localhost:8000",
        "127.0.0.1/8",
        "",
        "   ",
    ],
)
def test_non_local_targets_fail_closed(target):
    assert not check_target(target).allowed


def test_custom_allowlist_permits_cidr_membership():
    decision = check_target("10.1.2.3", allowed_targets=("10.0.0.0/8",))

    assert decision.allowed
    assert "10.0.0.0/8" in decision.reason


def test_empty_allowlist_blocks_loopback():
    assert not check_target("localhost", allowed_targets=()).allowed


def test_allowlist_does_not_resolve_dns():
    assert not check_target("localhost", allowed_targets=("evil.localhost",)).allowed


def test_unsupported_action_is_blocked():
    assert not check_action("exploit").allowed


@pytest.mark.parametrize("action", ["doctor", "scope-check", "demo", "report"])
def test_supported_actions_are_permitted(action):
    assert check_action(action).allowed


@pytest.mark.parametrize(
    "url",
    ["http://127.0.0.1:11434", "http://localhost:11434", "http://[::1]:11434", "https://127.0.0.1"],
)
def test_loopback_endpoints_are_allowed(url):
    assert check_endpoint(url).allowed


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "http://localhost.example.com:11434",
        "http://10.0.0.1:11434",
        "ftp://127.0.0.1",
        "http://",
        "",
    ],
)
def test_remote_endpoints_are_blocked(url):
    assert not check_endpoint(url).allowed
