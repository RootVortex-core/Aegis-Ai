from aegis.cli import main


def test_doctor_reports_readiness(capsys):
    assert main(["doctor"]) == 0

    output = capsys.readouterr().out
    assert "Runtime: ready" in output
    assert "Network scanning: disabled" in output
    assert "127.0.0.0/8" in output


def test_scope_check_blocks_external_target(capsys):
    assert main(["scope-check", "example.com"]) == 2
    assert "BLOCK" in capsys.readouterr().out


def test_scope_check_allows_localhost(capsys):
    assert main(["scope-check", "localhost"]) == 0
    assert "ALLOW" in capsys.readouterr().out


def test_demo_writes_report(tmp_path, capsys):
    output = tmp_path / "report.json"

    assert main(["demo", "--output", str(output)]) == 0

    assert output.exists()
    assert "Demo completed without network access." in capsys.readouterr().out


def test_demo_blocks_external_target(tmp_path, capsys):
    output = tmp_path / "report.json"

    assert main(["demo", "--target", "example.com", "--output", str(output)]) == 2

    assert not output.exists()
    assert "BLOCKED" in capsys.readouterr().err
