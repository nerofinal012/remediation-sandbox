import pytest

from remediator.errors import InvalidVersionError
from remediator.versions import is_vulnerable, parse_version


def test_parse_version_simple():
    assert parse_version("2.61.0") == (2, 61, 0)


def test_parse_version_strips_whitespace():
    assert parse_version(" 1.4.2\n") == (1, 4, 2)


def test_parse_version_empty_raises():
    with pytest.raises(InvalidVersionError):
        parse_version("   ")


@pytest.mark.parametrize(
    ("installed", "minimum", "expected"),
    [
        ("2.58.0", "2.61.0", True),
        ("2.61.0", "2.61.0", False),
        ("2.62.1", "2.61.0", False),
        ("2.9.0", "2.61.0", True),
    ],
)
def test_is_vulnerable_compares_numerically(installed, minimum, expected):
    assert is_vulnerable(installed, minimum) is expected
