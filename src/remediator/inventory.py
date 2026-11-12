"""Read what is installed on the host. All shell access goes through a CommandRunner."""

import logging

from remediator.platforms import build_installed_version_command
from remediator.runner import CommandRunner

logger = logging.getLogger(__name__)


def get_installed_version(runner: CommandRunner, package_manager: str, package: str) -> str | None:
    """Return the installed version of a package, or None if it is not installed."""
    result = runner.run(build_installed_version_command(package_manager, package))
    if result.returncode != 0:
        logger.info("package %s not installed (rc=%s)", package, result.returncode)
        return None
    version = result.stdout.strip()
    return version or None
