"""Custom exceptions for RSS fixer."""


class RSSFixerError(Exception):
    """Base exception for RSS fixer."""

    pass


class NoLinksFoundError(RSSFixerError):
    """Raised when no links are found during extraction."""

    pass


class NetworkError(RSSFixerError):
    """Raised when network requests fail."""

    pass


class FileWriteError(RSSFixerError):
    """Raised when unable to write output file."""

    pass


class JSONParsingError(RSSFixerError):
    """Raised when JSON parsing fails."""

    pass


class HTMLParsingError(RSSFixerError):
    """Raised when HTML parsing fails."""

    pass
