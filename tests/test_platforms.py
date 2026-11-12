import pytest

from remediator.errors import UnsupportedPlatformError
from remediator.platforms import (
    build_installed_version_command,
    build_upgrade_command,
    detect_package_manager,
    parse_os_release,
)


def test_parse_os_release_strips_quotes_and_comments():
    fields = parse_os_release('# comment\nNAME="Ubuntu"\nID=ubuntu\n\n')
    assert fields == {"NAME": "Ubuntu", "ID": "ubuntu"}


def test_detect_package_manager_ubuntu_is_apt(ubuntu_os_release):
    assert detect_package_manager(ubuntu_os_release) == "apt"


def test_detect_package_manager_uses_id_like():
    assert detect_package_manager("ID=linuxmint\nID_LIKE=\"ubuntu debian\"\n") == "apt"


def test_detect_package_manager_unknown_raises(alpine_os_release):
    with pytest.raises(UnsupportedPlatformError, match="alpine"):
        detect_package_manager(alpine_os_release)


@pytest.mark.parametrize(
    "text",
    [
        "ID=rhel\n",
        "ID=fedora\n",
        "ID=centos\n",
        "ID=amzn\n",
        'ID=rocky\nID_LIKE="rhel centos fedora"\n',
    ],
)
def test_detect_package_manager_rhel_family_is_dnf(text):
    assert detect_package_manager(text) == "dnf"


def test_detect_package_manager_dual_match_prefers_apt():
    assert detect_package_manager('ID=hybrid\nID_LIKE="debian rhel"\n') == "apt"


def test_detect_package_manager_does_not_match_substrings():
    with pytest.raises(UnsupportedPlatformError):
        detect_package_manager("ID=notrhel\n")


def test_detect_package_manager_unsupported_message_lists_all_managers(alpine_os_release):
    with pytest.raises(UnsupportedPlatformError) as exc_info:
        detect_package_manager(alpine_os_release)
    message = str(exc_info.value)
    assert "apt" in message
    assert "dnf" in message


def test_build_installed_version_command_apt():
    assert build_installed_version_command("apt", "acme-cli") == [
        "dpkg-query", "-W", "-f=${Version}", "acme-cli",
    ]


def test_build_installed_version_command_dnf():
    assert build_installed_version_command("dnf", "acme-cli") == [
        "rpm", "-q", "--qf", "%{VERSION}", "acme-cli",
    ]


def test_build_upgrade_command_apt_is_argument_list():
    assert build_upgrade_command("apt", "acme-cli") == [
        "apt-get", "install", "-y", "--only-upgrade", "acme-cli",
    ]


def test_build_upgrade_command_dnf_is_argument_list():
    command = build_upgrade_command("dnf", "acme-cli")
    assert isinstance(command, list)
    assert command == ["dnf", "upgrade", "-y", "acme-cli"]


def test_build_upgrade_command_unknown_manager_raises():
    with pytest.raises(UnsupportedPlatformError):
        build_upgrade_command("pacman", "acme-cli")
