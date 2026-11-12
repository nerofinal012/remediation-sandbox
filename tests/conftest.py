"""Shared fixtures. Tests never run real commands — use FakeRunner."""

from pathlib import Path

import pytest

from remediator.remediate import load_advisories
from remediator.runner import CommandResult

REPO_ROOT = Path(__file__).resolve().parents[1]

UBUNTU_OS_RELEASE = """\
NAME="Ubuntu"
VERSION_ID="22.04"
ID=ubuntu
ID_LIKE=debian
"""

ALPINE_OS_RELEASE = """\
NAME="Alpine Linux"
ID=alpine
"""


class FakeRunner:
    """Returns canned results keyed by the exact argument list, and records every call."""

    def __init__(self, responses: dict[tuple[str, ...], CommandResult] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[list[str]] = []

    def run(self, args: list[str]) -> CommandResult:
        self.calls.append(args)
        return self.responses.get(tuple(args), CommandResult(1, "", "not found"))


@pytest.fixture
def advisories():
    return load_advisories(REPO_ROOT / "advisories" / "advisories.json")


@pytest.fixture
def ubuntu_os_release():
    return UBUNTU_OS_RELEASE


@pytest.fixture
def alpine_os_release():
    return ALPINE_OS_RELEASE
