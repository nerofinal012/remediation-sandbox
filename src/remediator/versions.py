"""Version parsing and comparison. Pure functions, no I/O."""

import re

from remediator.errors import InvalidVersionError

Version = tuple[int, ...]

_NUMERIC = re.compile(r"\d+(?:\.\d+)*")
_EPOCH = re.compile(r"\d+")
_SUFFIX = re.compile(r"(?:~[0-9A-Za-z.]+)?(?:\+[0-9A-Za-z.+~]+)?")


def _split_epoch(text: str) -> tuple[int, str]:
    """Split an optional 'N:' epoch prefix from the rest of the version."""
    if ":" not in text:
        return 0, text
    epoch, rest = text.split(":", 1)
    if not _EPOCH.fullmatch(epoch):
        raise InvalidVersionError(f"invalid epoch in version {text!r}")
    return int(epoch), rest


def _strip_revision(text: str) -> str:
    """Remove the Debian revision (text after the last '-')."""
    if "-" not in text:
        return text
    upstream, revision = text.rsplit("-", 1)
    if not revision or not re.fullmatch(r"[0-9A-Za-z.+~]+", revision):
        raise InvalidVersionError(f"invalid revision in version {text!r}")
    return upstream


def parse_version(text: str) -> Version:
    """Parse a version such as '1:2.61.0-1ubuntu1' into a comparable tuple."""
    cleaned = text.strip()
    if not cleaned:
        raise InvalidVersionError("empty version string")
    epoch, rest = _split_epoch(cleaned)
    upstream = _strip_revision(rest)
    match = _NUMERIC.match(upstream)
    if match is None or not _SUFFIX.fullmatch(upstream[match.end():]):
        raise InvalidVersionError(f"invalid version string {text!r}")
    numbers = [int(part) for part in match.group(0).split(".")]
    while numbers and numbers[-1] == 0:
        numbers.pop()
    marker = -1 if "~" in upstream[match.end():] else 0
    # Trailing zeros are dropped so 2.61 == 2.61.0; the marker is placed after the
    # numbers, and a pre-release must sort before any further component, so use
    # a sentinel layout: (epoch, *numbers, marker) with marker -1 < any component >= 0.
    return (epoch, *numbers, marker)


def is_vulnerable(installed: str, minimum_safe: str) -> bool:
    """Return True when the installed version is older than the minimum safe version."""
    return parse_version(installed) < parse_version(minimum_safe)
