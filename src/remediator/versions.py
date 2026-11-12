"""Version parsing and comparison. Pure functions, no I/O."""

from remediator.errors import InvalidVersionError

Version = tuple[int, ...]


def parse_version(text: str) -> Version:
    """Parse a dotted version string such as '2.61.0' into a comparable tuple."""
    cleaned = text.strip()
    if not cleaned:
        raise InvalidVersionError("empty version string")
    return tuple(int(part) for part in cleaned.split("."))


def is_vulnerable(installed: str, minimum_safe: str) -> bool:
    """Return True when the installed version is older than the minimum safe version."""
    return parse_version(installed) < parse_version(minimum_safe)
