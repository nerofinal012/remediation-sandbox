"""Decide what remediation, if any, a host needs. No direct subprocess calls."""

import json
from dataclasses import dataclass
from pathlib import Path

from remediator.errors import AdvisoryNotFoundError
from remediator.inventory import get_installed_version
from remediator.platforms import build_upgrade_command, detect_package_manager
from remediator.runner import CommandRunner
from remediator.versions import is_vulnerable


@dataclass(frozen=True)
class Advisory:
    """A single advisory: a package and the minimum version that is safe."""

    id: str
    package: str
    minimum_safe_version: str
    severity: str


@dataclass(frozen=True)
class RemediationPlan:
    """What should happen for one package on one host."""

    package: str
    action: str  # "none" | "upgrade" | "not_installed"
    installed_version: str | None
    minimum_safe_version: str
    advisory_id: str
    command: list[str] | None = None


def load_advisories(path: Path) -> dict[str, Advisory]:
    """Load the advisory feed and index it by package name."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        item["package"]: Advisory(
            id=item["id"],
            package=item["package"],
            minimum_safe_version=item["minimum_safe_version"],
            severity=item["severity"],
        )
        for item in raw["advisories"]
    }


def plan_remediation(
    package: str,
    advisories: dict[str, Advisory],
    runner: CommandRunner,
    os_release_text: str,
) -> RemediationPlan:
    """Build a remediation plan for one package on the current host."""
    advisory = advisories.get(package)
    if advisory is None:
        raise AdvisoryNotFoundError(f"no advisory for package {package!r}")

    package_manager = detect_package_manager(os_release_text)
    installed = get_installed_version(runner, package_manager, package)
    base = {
        "package": package,
        "installed_version": installed,
        "minimum_safe_version": advisory.minimum_safe_version,
        "advisory_id": advisory.id,
    }
    if installed is None:
        return RemediationPlan(action="not_installed", **base)
    if is_vulnerable(installed, advisory.minimum_safe_version):
        command = build_upgrade_command(package_manager, package)
        return RemediationPlan(action="upgrade", command=command, **base)
    return RemediationPlan(action="none", **base)
