import pytest

from conftest import FakeRunner
from remediator.errors import AdvisoryNotFoundError
from remediator.remediate import plan_remediation
from remediator.runner import CommandResult

DPKG_QUERY = ("dpkg-query", "-W", "-f=${Version}", "acme-cli")


def test_plan_remediation_vulnerable_returns_upgrade(advisories, ubuntu_os_release):
    runner = FakeRunner({DPKG_QUERY: CommandResult(0, "2.58.0", "")})
    plan = plan_remediation("acme-cli", advisories, runner, ubuntu_os_release)
    assert plan.action == "upgrade"
    assert plan.command == ["apt-get", "install", "-y", "--only-upgrade", "acme-cli"]
    assert plan.advisory_id == "FAKE-2026-0101"


def test_plan_remediation_safe_version_returns_none(advisories, ubuntu_os_release):
    runner = FakeRunner({DPKG_QUERY: CommandResult(0, "2.61.0", "")})
    plan = plan_remediation("acme-cli", advisories, runner, ubuntu_os_release)
    assert plan.action == "none"
    assert plan.command is None


def test_plan_remediation_not_installed(advisories, ubuntu_os_release):
    runner = FakeRunner()  # every command "fails" -> not installed
    plan = plan_remediation("acme-cli", advisories, runner, ubuntu_os_release)
    assert plan.action == "not_installed"
    assert plan.installed_version is None


def test_plan_remediation_unknown_package_raises(advisories, ubuntu_os_release):
    with pytest.raises(AdvisoryNotFoundError):
        plan_remediation("does-not-exist", advisories, FakeRunner(), ubuntu_os_release)


def test_plan_remediation_never_runs_upgrade_itself(advisories, ubuntu_os_release):
    runner = FakeRunner({DPKG_QUERY: CommandResult(0, "2.58.0", "")})
    plan_remediation("acme-cli", advisories, runner, ubuntu_os_release)
    assert runner.calls == [list(DPKG_QUERY)]
