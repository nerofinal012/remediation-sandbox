"""Exceptions raised by remediator."""


class RemediatorError(Exception):
    """Base class for all remediator errors."""


class InvalidVersionError(RemediatorError):
    """A version string could not be parsed."""


class UnsupportedPlatformError(RemediatorError):
    """The host OS or package manager is not supported."""


class AdvisoryNotFoundError(RemediatorError):
    """No advisory exists for the requested package."""
