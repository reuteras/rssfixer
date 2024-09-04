"""Generate rss feed for "blogs" without rss feed."""

import argparse
import hashlib
import importlib.metadata
import json
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator

try:
    __version__ = "version " + importlib.metadata.version(__package__ or __name__)
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

ua = (
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


def fetch_html(arguments):
    """Fetch HTML content from a URL."""
    url = arguments.url
    headers = {
        "User-Agent": arguments.user_agent,
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.Timeout:  # pragma: no cover
        print("ERROR: Request timed out")
        sys.exit(1)
    except requests.exceptions.ConnectionError:  # pragma: no cover
        print("ERROR: Unable to connect to server")
        sys.exit(1)
    return response.text


def find_entries(json_object, entries_key):
    """Find the entries in a JSON object with key "entries_key"."""
    if isinstance(json_object, dict):
        for key, value in json_object.items():
            if key == entries_key:
                return value
            result = find_entries(value, entries_key)
            if result is not None:
                return result
    elif isinstance(json_object, list):
        for item in json_object:
            result = find_entries(item, entries_key)
            if result is not None:
                return result
    return None


def filter_html(soup, filter_type, filter_name):
    """Filter web page."""
    if filter_name is None:
        filtersoup = soup.find_all(filter_type)
    else:
        filtersoup = soup.find_all(filter_type, filter_name)
    if not filtersoup:
        print("ERROR: No entries found")
        sys.exit(1)
    filtersoup = BeautifulSoup(str(filtersoup), "html.parser")
    return filtersoup


def extract_links_ul(soup):
    """Extract links from an HTML page with links in <ul>-lists."""
    links = []
    unique_links = set()

    # Iterate through all the <ul> elements in the page
    for links_list in soup.find_all("ul", class_=None):
        for li in links_list.find_all("li"):
            link = li.find("a")
            if link:
                url = link["href"]
                title = link.text.strip()
                description = link.text.strip()

                # Exclude URLs containing "/category/" or "/author/"
                if "/category/" not in url and "/author/" not in url:
                    # Check if the URL is unique
                    if url not in unique_links:
                        unique_links.add(url)
                        links.append((url, title, description))

    if not links:
        print("ERROR: No links found")
        sys.exit(1)
    return links


def get_html_title(entry, arguments):
    """Get the title of an HTML page."""
    if arguments.html_title_class:
        title = entry.find(
            arguments.html_title,
            re.compile(arguments.html_title_class),
        ).text.strip()
    else:
        title = entry.find(arguments.html_title).text.strip()
    return title


def extract_links_html(soup, arguments):
    """Extract links from an HTML page with links in selectable elements."""
    links = []
    unique_links = set()

    # Iterate through all the elements of type html_entries in the page
    for entry in soup.find_all(arguments.html_entries, arguments.html_entries_class):
        try:
            url = entry.find_all(arguments.html_url)[0]["href"]
            title = get_html_title(entry, arguments)
        except (KeyError, AttributeError):
            # Continue if URL or title is not found to find other entries
            continue
        try:
            if not arguments.html_description_class:
                description = entry.find(arguments.html_description).text.strip()
            else:
                description = entry.find(
                    arguments.html_description,
                    re.compile(arguments.html_description_class),
                ).text.strip()
        except (KeyError, AttributeError):
            # Ignore description if it's not found
            description = ""
        if url not in unique_links:
            if arguments.title_filter:
                if re.search(arguments.title_filter, title):
                    unique_links.add(url)
                    links.append((url, title, description))
            else:
                unique_links.add(url)
                links.append((url, title, description))

    if not links:
        print("ERROR: No links found")
        sys.exit(1)
    return links


def extract_links_json(soup, arguments):
    """Extract links from JSON strings in an HTML page."""
    entries = None
    links = []
    unique_links = set()

    # Find the JSON string in the page
    for json_text in soup.find_all("script", type="application/json"):
        json_object = json.loads(json_text.text)
        entries = find_entries(json_object, arguments.json_entries)
        if entries is not None:
            break

    if entries is None:
        print("ERROR: Unable to find JSON object")
        sys.exit(1)

    # Extract the links from the JSON object
    for entry in entries:
        try:
            url = entry[arguments.json_url]
            title = entry[arguments.json_title]
        except KeyError:
            print("ERROR: Unable to find URL or title in JSON object")
            sys.exit(1)
        try:
            description = entry[arguments.json_description]
        except KeyError:
            # Ignore description if it's not found
            description = ""
        if url not in unique_links:
            unique_links.add(url)
            links.append((url, title, description))

    return links


def extract_links_release(soup, arguments):
    """Extract links from an html page with one type of html entries."""
    links = []
    unique_titles = set()

    # Iterate through all the elements of type html_entries in the page
    for entry in soup.find_all(arguments.release_entries):
        try:
            title = entry.text.strip()
            if not title:
                raise AttributeError
            title_bytes = title.encode("utf-8")
            title_hash = hashlib.sha256(title_bytes)
            title_sha256 = title_hash.hexdigest()
            url = arguments.release_url + "?" + title_sha256
        except (KeyError, AttributeError):
            print("ERROR: Unable to title in HTML element")
            sys.exit(1)
        description = ""
        if title not in unique_titles:
            unique_titles.add(title)
            links.append((url, title, description))

    if not links:
        print("ERROR: No titles found")
        sys.exit(1)
    return links


def create_rss_feed(links, arguments):
    """Create an RSS feed from a list of links."""
    feed_description = f"RSS feed generated from the links at {arguments.url}"

    # Create the RSS feed
    fg = FeedGenerator()
    fg.id(arguments.url)
    fg.title(arguments.title)
    fg.description(feed_description)
    fg.link(href=arguments.url, rel="alternate")

    # Add entries to the RSS feed
    for url, title, description in links:
        fe = fg.add_entry()
        fe_url = url
        if arguments.base_url:
            if not url.startswith("http"):
                fe_url = arguments.base_url + url
        fe.link(href=fe_url)
        fe.id(fe_url)
        fe.title(title)
        if vars(arguments).get("atom", False):
            fe.summary(description)
            fe.content(content=description, src=url)
        else:
            fe.description(description)

    if vars(arguments).get("atom", False):
        return fg.atom_str(pretty=True).decode("utf-8")
    return fg.rss_str(pretty=True).decode("utf-8")


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
        default=ua,
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


def save_rss_feed(rss_feed, arguments):
    """Save the RSS feed to a file."""
    try:
        with Path.open(arguments.output, "w", encoding="utf-8") as f:
            f.write(rss_feed)
    except OSError:
        print("ERROR: Unable to write to file")
        sys.exit(1)

    if not arguments.quiet:
        if arguments.atom:
            print(f"Atom feed created: {arguments.output}")
        else:
            print(f"RSS feed created: {arguments.output}")


def main(args=None):
    """Handle program arguments."""
    if args is None:
        args = sys.argv[1:]

    args = parse_arguments(args)

    if vars(args).get("version"):
        print(__version__)
        sys.exit(0)

    # Get HTML content from URL
    html_content = fetch_html(args)
    soup = BeautifulSoup(html_content, "html.parser")

    # Filter web page
    if args.filter_type and args.filter_name:
        soup = filter_html(soup, args.filter_type, args.filter_name)
    if args.debug:
        print("DEBUG: Filtered HTML\n")
        print(soup.prettify())

    # Select function to handle different types of blogs
    if args.json:
        links = extract_links_json(soup, args)
    elif args.html:
        links = extract_links_html(soup, args)
    elif args.list:
        links = extract_links_ul(soup)
    elif args.release:
        if not vars(args).get("release_url", False):
            print("ERROR: Release URL not specified")
            sys.exit(1)
        links = extract_links_release(soup, args)
    else:
        print("ERROR: No valid blog type specified")
        sys.exit(1)

    # Create RSS feed and save to file
    rss_feed = create_rss_feed(links, args)
    if args.stdout:
        print(rss_feed)
    else:
        save_rss_feed(rss_feed, args)


def init():
    """Initialize the script."""
    if __name__ == "__main__":
        sys.exit(main())


init()
