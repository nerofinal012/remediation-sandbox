"""Map an OS to its package manager and build upgrade commands. Pure functions, no I/O."""

from remediator.errors import UnsupportedPlatformError

SUPPORTED_PACKAGE_MANAGERS = ("apt",)

_APT_DISTRO_IDS = {"debian", "ubuntu"}


def parse_os_release(text: str) -> dict[str, str]:
    """Parse the contents of /etc/os-release into a dict."""
    fields: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        fields[key.strip()] = value.strip().strip('"')
    return fields


def detect_package_manager(os_release_text: str) -> str:
    """Return the package manager for the host described by /etc/os-release."""
    fields = parse_os_release(os_release_text)
    ids = {fields.get("ID", "").lower(), *fields.get("ID_LIKE", "").lower().split()}
    if ids & _APT_DISTRO_IDS:
        return "apt"
    raise UnsupportedPlatformError(
        f"unsupported platform ID={fields.get('ID', '?')!r}; "
        f"supported package managers: {', '.join(SUPPORTED_PACKAGE_MANAGERS)}"
    )


def build_installed_version_command(package_manager: str, package: str) -> list[str]:
    """Return the command that prints the installed version of a package."""
    if package_manager == "apt":
        return ["dpkg-query", "-W", "-f=${Version}", package]
    raise UnsupportedPlatformError(f"unsupported package manager: {package_manager!r}")


def build_upgrade_command(package_manager: str, package: str) -> list[str]:
    """Return the command that upgrades a package to the latest available version."""
    if package_manager == "apt":
        return ["apt-get", "install", "-y", "--only-upgrade", package]
    raise UnsupportedPlatformError(f"unsupported package manager: {package_manager!r}")
