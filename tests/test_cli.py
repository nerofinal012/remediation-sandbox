from conftest import UBUNTU_OS_RELEASE, FakeRunner
from remediator import cli
from remediator.runner import CommandResult

DPKG_QUERY = ("dpkg-query", "-W", "-f=${Version}", "acme-cli")
APT_UPGRADE = ("apt-get", "install", "-y", "--only-upgrade", "acme-cli")


def _use_ubuntu(monkeypatch, tmp_path):
    os_release = tmp_path / "os-release"
    os_release.write_text(UBUNTU_OS_RELEASE, encoding="utf-8")
    monkeypatch.setattr(cli, "OS_RELEASE_PATH", os_release)


def test_cli_dry_run_does_not_upgrade(monkeypatch, tmp_path, capsys):
    _use_ubuntu(monkeypatch, tmp_path)
    runner = FakeRunner({DPKG_QUERY: CommandResult(0, "2.58.0", "")})
    assert cli.main(["--package", "acme-cli"], runner=runner) == 0
    assert list(APT_UPGRADE) not in runner.calls
    assert "VULNERABLE" in capsys.readouterr().out


def test_cli_apply_runs_upgrade(monkeypatch, tmp_path):
    _use_ubuntu(monkeypatch, tmp_path)
    runner = FakeRunner({
        DPKG_QUERY: CommandResult(0, "2.58.0", ""),
        APT_UPGRADE: CommandResult(0, "", ""),
    })
    assert cli.main(["--package", "acme-cli", "--apply"], runner=runner) == 0
    assert list(APT_UPGRADE) in runner.calls


def test_cli_unknown_package_exits_2(monkeypatch, tmp_path, capsys):
    _use_ubuntu(monkeypatch, tmp_path)
    assert cli.main(["--package", "nope"], runner=FakeRunner()) == 2
    assert "no advisory" in capsys.readouterr().err


def test_cli_debian_revision_reports_vulnerable(monkeypatch, tmp_path, capsys):
    _use_ubuntu(monkeypatch, tmp_path)
    runner = FakeRunner({DPKG_QUERY: CommandResult(0, "2.58.0-1ubuntu1", "")})
    assert cli.main(["--package", "acme-cli"], runner=runner) == 0
    out = capsys.readouterr().out
    assert (
        "acme-cli 2.58.0-1ubuntu1: VULNERABLE (FAKE-2026-0101, needs >= 2.61.0) -> "
        "apt-get install -y --only-upgrade acme-cli"
    ) in out
    assert list(APT_UPGRADE) not in runner.calls


def test_cli_malformed_installed_version_exits_2_without_traceback(monkeypatch, tmp_path, capsys):
    _use_ubuntu(monkeypatch, tmp_path)
    runner = FakeRunner({DPKG_QUERY: CommandResult(0, "not-a-version", "")})
    assert cli.main(["--package", "acme-cli"], runner=runner) == 2
    assert capsys.readouterr().err.startswith("error:")
