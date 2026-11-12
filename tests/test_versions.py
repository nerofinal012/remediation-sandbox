import pytest

from remediator.errors import InvalidVersionError
from remediator.versions import is_vulnerable, parse_version


def test_parse_version_simple():
    assert parse_version("2.61.0")[1:3] == (2, 61)
    assert parse_version("2.61.0") == parse_version("2.61")


def test_parse_version_strips_whitespace():
    assert parse_version(" 1.4.2\n") == parse_version("1.4.2")


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


def test_parse_version_debian_revision_does_not_raise():
    assert parse_version("2.58.0-1ubuntu1") == parse_version("2.58.0")


def test_is_vulnerable_revision_suffix_compared_upstream_only():
    assert is_vulnerable("2.58.0-1ubuntu1", "2.61.0") is True
    assert is_vulnerable("2.61.0-1ubuntu1", "2.61.0") is False


def test_parse_version_epoch_is_parsed():
    assert parse_version("1:2.58.0-1ubuntu1")[0] == 1


def test_is_vulnerable_epoch_takes_precedence():
    assert is_vulnerable("1:2.58.0-1ubuntu1", "2.61.0") is False
    assert is_vulnerable("0:2.58.0", "2.61.0") is True


def test_is_vulnerable_tilde_prerelease_older_than_release():
    assert is_vulnerable("2.61.0~rc1", "2.61.0") is True
    assert is_vulnerable("2.61.0+dfsg-1", "2.61.0") is False


def test_is_vulnerable_trailing_zero_padding_and_tilde_short_form():
    assert is_vulnerable("2.61", "2.61.0") is False
    assert is_vulnerable("2.61.0", "2.61") is False
    assert is_vulnerable("2.61~rc1", "2.61.0") is True


@pytest.mark.parametrize(
    "text", ["abc", "2..0", "2.x.0", "x:2.0", "1:", "2.58.0-", "2.58.0 beta"]
)
def test_parse_version_malformed_raises_invalid_version_error(text):
    with pytest.raises(InvalidVersionError):
        parse_version(text)


def test_is_vulnerable_malformed_minimum_safe_raises():
    with pytest.raises(InvalidVersionError):
        is_vulnerable("2.58.0", "garbage")


def test_is_vulnerable_plain_versions_unchanged():
    assert parse_version("2.9.0") < parse_version("2.61.0")
