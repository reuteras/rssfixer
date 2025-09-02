"""Command line interface and argument parsing."""

import argparse
import importlib.metadata

from .exceptions import RSSFixerError
from .extractors import HtmlExtractor, JsonExtractor, ListExtractor, ReleaseExtractor

try:
    __version__ = "version " + importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
)


class CheckHtmlAction(argparse.Action):
    """Class to validate argparse for --html options."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Validate the class."""
        if not namespace.html:
            parser.error(f"{option_string} requires --html to be specified.")
        setattr(namespace, self.dest, values)


class CheckJsonAction(argparse.Action):
    """Class to validate argparse for --json options."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Validate the class."""
        if not namespace.json:
            parser.error(f"{option_string} requires --json to be specified.")
        setattr(namespace, self.dest, values)


class CheckReleaseAction(argparse.Action):
    """Class to validate argparse for --release options."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Validate the class."""
        if not namespace.release:
            parser.error(f"{option_string} requires --release to be specified.")
        setattr(namespace, self.dest, values)


def parse_arguments(arguments):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="""Generate RSS feed for blog that don't publish a feed.
        Default is to find links in a simple <ul>-list.
        Options are available to find links in other HTML elements or JSON strings.""",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--html", action="store_true", help="Find entries in HTML")
    group.add_argument("--json", action="store_true", help="Find entries in JSON")
    group.add_argument(
        "--list",
        action="store_true",
        help="Find entries in HTML <ul>-list (default)",
    )
    group.add_argument("--release", action="store_true", help="Find releases in HTML")

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )
    parser.add_argument("url", help="URL for the blog")
    parser.add_argument("--atom", action="store_true", help="Generate Atom feed")
    parser.add_argument("--base-url", help="Base URL for the blog")
    parser.add_argument(
        "--release-url",
        action=CheckReleaseAction,
        help="Release URL for downloads",
    )
    parser.add_argument(
        "--release-entries",
        action=CheckReleaseAction,
        help="Release selector for entries",
    )
    parser.add_argument(
        "--html-entries",
        action=CheckHtmlAction,
        default="article",
        help="HTML selector for entries",
    )
    parser.add_argument(
        "--html-entries-class",
        action=CheckHtmlAction,
        default="",
        help="Class name for entries",
    )
    parser.add_argument(
        "--html-url",
        action=CheckHtmlAction,
        default="a",
        help="HTML selector for URL",
    )
    parser.add_argument(
        "--html-title",
        action=CheckHtmlAction,
        default="h3",
        help="HTML selector for title",
    )
    parser.add_argument(
        "--html-title-class",
        action=CheckHtmlAction,
        default="title",
        help="Flag to specify title class (regex)",
    )
    parser.add_argument(
        "--title-filter",
        help="Filter for title, ignore entries that don't match",
    )
    parser.add_argument(
        "--html-description",
        action=CheckHtmlAction,
        default="div",
        help="HTML selector for description",
    )
    parser.add_argument(
        "--html-description-class",
        action=CheckHtmlAction,
        default="summary",
        help="Flag to specify description class (regex)",
    )
    parser.add_argument(
        "--json-entries",
        action=CheckJsonAction,
        default="entries",
        help="JSON key for entries (default: 'entries')",
    )
    parser.add_argument(
        "--json-url",
        action=CheckJsonAction,
        default="url",
        help="JSON key for URL (default: 'url')",
    )
    parser.add_argument(
        "--json-title",
        action=CheckJsonAction,
        default="title",
        help="JSON key for title",
    )
    parser.add_argument(
        "--json-description",
        action=CheckJsonAction,
        default="description",
        help="JSON key for description",
    )
    parser.add_argument(
        "--output",
        default="rss_feed.xml",
        help="Name of the output file",
    )
    parser.add_argument(
        "--title",
        default="My RSS Feed",
        help='Title of the RSS feed (default: "My RSS Feed")',
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="User agent to use for HTTP requests",
    )
    parser.add_argument(
        "--filter-type",
        help="Filter web page",
    )
    parser.add_argument(
        "--filter-name",
        help="Filter web page",
    )

    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    parser.add_argument("-d", "--debug", action="store_true", help="Debug selection")
    parser.add_argument("--stdout", action="store_true", help="Print to stdout")

    return parser.parse_args(arguments)


def get_extractor(arguments) -> HtmlExtractor | JsonExtractor | ListExtractor | ReleaseExtractor:
    """Get appropriate extractor based on arguments.

    Args:
        arguments: Parsed command line arguments

    Returns:
        Appropriate LinkExtractor instance

    Raises:
        RSSFixerError: If no valid extractor type specified or missing required arguments

    """
    if arguments.json:
        return JsonExtractor(arguments)
    elif arguments.html:
        return HtmlExtractor(arguments)
    elif arguments.list:
        return ListExtractor(arguments)
    elif arguments.release:
        if not getattr(arguments, "release_url", False):
            raise RSSFixerError("Release URL not specified")
        return ReleaseExtractor(arguments)
    else:
        raise RSSFixerError("No valid blog type specified")
