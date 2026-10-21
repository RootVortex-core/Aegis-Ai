from aegis.policy import check_action, check_target


def test_localhost_is_allowlisted():
    assert check_target("localhost").allowed


def test_external_target_fails_closed():
    assert not check_target("example.com").allowed


def test_unsupported_action_is_blocked():
    assert not check_action("exploit").allowed
