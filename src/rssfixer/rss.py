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
from test.test_hashlib import HASH

try:
    __version__: str = "version " + importlib.metadata.version(distribution_name=__package__ or __name__)
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
            parser.error(message=f"{option_string} requires --html to be specified.")
        setattr(namespace, self.dest, values)


class CheckJsonAction(argparse.Action):
    """Class to validate argparse for --json options."""

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        """Validate the class."""
        if not namespace.json:
            parser.error(message=f"{option_string} requires --json to be specified.")
        setattr(namespace, self.dest, values)


class CheckReleaseAction(argparse.Action):
    """Class to validate argparse for --release options."""

    def __call__(self, parser, namespace, values, option_string=None) -> None:
        """Validate the class."""
        if not namespace.release:
            parser.error(message=f"{option_string} requires --release to be specified.")
        setattr(namespace, self.dest, values)


def fetch_html(arguments) -> str:
    """Fetch HTML content from a URL."""
    url = arguments.url
    headers = {
        "User-Agent": arguments.user_agent,
    }
    try:
        response: requests.Response = requests.get(url=url, headers=headers, timeout=10)
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
            result = find_entries(json_object=value, entries_key=entries_key)
            if result is not None:
                return result
    elif isinstance(json_object, list):
        for item in json_object:
            result = find_entries(json_object=item, entries_key=entries_key)
            if result is not None:
                return result
    return None


def filter_html(soup, filter_type, filter_name) -> BeautifulSoup:
    """Filter web page."""
    if filter_name is None:
        filtersoup = soup.find_all(filter_type)
    else:
        filtersoup = soup.find_all(filter_type, filter_name)
    if not filtersoup:
        print("ERROR: No entries found")
        sys.exit(1)
    filtersoup = BeautifulSoup(markup=str(object=filtersoup), features="html.parser")
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
                try:
                    url = link.get("href")
                    if not url:
                        url = ""
                except KeyError:
                    url = ""
                    continue
                title: str = link.text.strip()
                description: str = link.text.strip()

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
            re.compile(pattern=arguments.html_title_class),
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
            title = get_html_title(entry=entry, arguments=arguments)
        except (KeyError, AttributeError):
            # Continue if URL or title is not found to find other entries
            continue
        try:
            if not arguments.html_description_class:
                description = entry.find(arguments.html_description).text.strip()
            else:
                description = entry.find(
                    arguments.html_description,
                    re.compile(pattern=arguments.html_description_class),
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
        entries = find_entries(json_object=json_object, entries_key=arguments.json_entries)
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
            title_hash: HASH = hashlib.sha256(title_bytes)
            title_sha256: str = title_hash.hexdigest()
            url = arguments.release_url + "?" + title_sha256
        except (KeyError, AttributeError):
            print("ERROR: Unable to title in HTML element")
            sys.exit(1)
        description: str = ""
        if title not in unique_titles:
            unique_titles.add(title)
            links.append((url, title, description))

    if not links:
        print("ERROR: No titles found")
        sys.exit(1)
    return links


def detect_extraction_method(soup, url):  # noqa: PLR0912
    """Auto-detect the best extraction method for a given page."""
    # Check for JSON data
    json_scripts = soup.find_all("script", type="application/json")
    if json_scripts:
        # Try to find common entry patterns in JSON
        for script in json_scripts:
            try:
                data = json.loads(script.text)
                entries = None

                # Look for common JSON patterns
                for key in ["entries", "posts", "items", "results", "data"]:
                    entries = find_entries(json_object=data, entries_key=key)
                    if entries and isinstance(entries, list) and len(entries) > 0:
                        # Look for common URL and title keys
                        url_keys: list[str] = ["url", "link", "href", "permalink"]
                        title_keys: list[str] = ["title", "headline", "name"]

                        # Check if entries have these keys
                        sample = entries[0]
                        found_url: str | None = None
                        found_title: str | None = None

                        for uk in url_keys:
                            if uk in sample:
                                found_url = uk
                                break

                        for tk in title_keys:
                            if tk in sample:
                                found_title = tk
                                break

                        if found_url and found_title:
                            return {
                                "method": "json",
                                "json_entries": key,
                                "json_url": found_url,
                                "json_title": found_title,
                            }
            except (json.JSONDecodeError, AttributeError):
                continue

    # Check for common blog structures
    # Look for article, div, or li elements with titles and links
    for entry_tag in ["article", "div.post", "div.entry", "div.item", "li.post"]:
        tag, *classes = entry_tag.split(sep=".")
        if classes:
            entries = soup.find_all(tag, class_=classes[0])
        else:
            entries = soup.find_all(tag)

        if len(entries) >= 3:  # Require at least 3 entries to be confident  # noqa: PLR2004
            # Check if these have titles and links
            for entry in entries[:3]:  # Check just the first 3
                title_tag = entry.find(["h1", "h2", "h3", "h4", "h5"])
                link = entry.find("a")

                if title_tag and link and link.get("href"):
                    # We found a likely blog structure
                    return {
                        "method": "html",
                        "html_entries": tag,
                        "html_entries_class": classes[0] if classes else "",
                        "html_url": "a",
                        "html_title": title_tag.name,
                    }

    # Check for link lists
    link_lists = []
    for ul in soup.find_all("ul"):
        links = ul.find_all("a")
        if len(links) >= 5:  # Look for ULs with a significant number of links  # noqa: PLR2004
            link_lists.append((ul, len(links)))

    if link_lists:
        # Sort by number of links, descending
        link_lists.sort(key=lambda x: x[1], reverse=True)
        return {
            "method": "list",
        }

    # If all else fails, try to find any links on the page
    all_links = soup.find_all("a")
    if all_links:
        return {
            "method": "list",
        }

    return None  # Could not detect a suitable method


def create_rss_feed(links, arguments):
    """Create an RSS feed from a list of links."""
    feed_description = f"RSS feed generated from the links at {arguments.url}"

    # Create the RSS feed
    fg = FeedGenerator()
    fg.id(id=arguments.url)
    fg.title(title=arguments.title)
    fg.description(description=feed_description)
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


def parse_arguments(arguments) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="""Generate RSS feed for websites that don't publish a feed.
        Will attempt to auto-detect the appropriate extraction method if none is specified.""",
    )

    # Mode selection (mutually exclusive)
    mode_group: argparse._MutuallyExclusiveGroup = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--auto",
        action="store_true",
        default=True,
        help="Auto-detect the best extraction method (default)",
    )
    mode_group.add_argument("--html", action="store_true", help="Find entries in HTML elements")
    mode_group.add_argument("--json", action="store_true", help="Find entries in JSON")
    mode_group.add_argument("--list", action="store_true", help="Find entries in HTML <ul>-lists")
    mode_group.add_argument("--release", action="store_true", help="Find software releases")

    # Basic settings
    parser.add_argument("url", help="URL of the website")
    parser.add_argument("--output", default="rss_feed.xml", help="Output file (default: rss_feed.xml)")
    parser.add_argument("--title", help="Title of the RSS feed (default: extracted from page)")
    parser.add_argument("--base-url", help="Base URL for relative links")
    parser.add_argument("--atom", action="store_true", help="Generate Atom feed instead of RSS")

    # Site templates
    parser.add_argument(
        "--site",
        choices=["wordpress", "medium", "github", "custom"],
        help="Use predefined settings for common site types",
    )

    # Advanced options group
    advanced: argparse._ArgumentGroup = parser.add_argument_group(title="Advanced Options")

    # HTML options
    html_group: argparse._ArgumentGroup = advanced.add_argument_group(title="HTML Options")
    html_group.add_argument("--html-entries", help="HTML selector for entries (default: article)")
    html_group.add_argument("--html-entries-class", help="Class name for entries")
    html_group.add_argument("--html-url", help="HTML selector for URL (default: a)")
    html_group.add_argument("--html-title", help="HTML selector for title (default: h3)")
    html_group.add_argument("--html-title-class", help="Title element class (regex)")
    html_group.add_argument("--html-description", help="HTML selector for description (default: div)")
    html_group.add_argument("--html-description-class", help="Description class (regex)")

    # JSON options
    json_group: argparse._ArgumentGroup = advanced.add_argument_group(title="JSON Options")
    json_group.add_argument("--json-entries", help="JSON key for entries array (default: entries)")
    json_group.add_argument("--json-url", help="JSON key for URL (default: url)")
    json_group.add_argument("--json-title", help="JSON key for title (default: title)")
    json_group.add_argument("--json-description", help="JSON key for description (default: description)")

    # Release options
    release_group: argparse._ArgumentGroup = advanced.add_argument_group(title="Release Options")
    release_group.add_argument("--release-url", help="Base URL for releases")
    release_group.add_argument("--release-entries", help="Selector for release entries")

    # Filtering options
    filter_group: argparse._ArgumentGroup = advanced.add_argument_group(title="Filtering Options")
    filter_group.add_argument("--title-filter", help="Regex to filter entries by title")
    filter_group.add_argument("--filter-type", help="Filter webpage by element type")
    filter_group.add_argument("--filter-name", help="Filter webpage by element name/class")

    # Other options
    parser.add_argument("--user-agent", default=ua, help="User agent for HTTP requests")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    parser.add_argument("-d", "--debug", action="store_true", help="Debug mode")
    parser.add_argument("--stdout", action="store_true", help="Output to stdout")
    parser.add_argument("--version", action="version", version="%(prog)s " + __version__)

    args: argparse.Namespace = parser.parse_args(args=arguments)

    # Apply site-specific templates
    if args.site:
        apply_site_template(args)

    return args


def apply_site_template(args) -> None:
    """Apply site-specific templates to simplify configuration."""
    templates = {
        "wordpress": {
            "html": True,
            "html_entries": "article",
            "html_title": "h2",
            "html_url": "a",
            "html_description": "div",
            "html_description_class": "entry-summary",
        },
        "medium": {
            "html": True,
            "html_entries": "article",
            "html_title": "h3",
            "html_url": "a",
            "filter_type": "div",
            "filter_name": "js-postsList",
        },
        "github": {
            "release": True,
            "html_entries": "div.release-entry",
            "html_title": "a.Link--primary",
            "html_url": "a.Link--primary",
            "html_description": "div.markdown-body",
        },
    }

    if args.site in templates:
        # Apply template settings
        template = templates[args.site]
        for key, value in template.items():
            if not getattr(args, key, None):  # Only set if not already set by user
                setattr(args, key, value)


def save_rss_feed(rss_feed, arguments):
    """Save the RSS feed to a file."""
    try:
        with Path.open(arguments.output, mode="w", encoding="utf-8") as f:
            f.write(rss_feed)
    except OSError:
        print("ERROR: Unable to write to file")
        sys.exit(1)

    if not arguments.quiet:
        if arguments.atom:
            print(f"Atom feed created: {arguments.output}")
        else:
            print(f"RSS feed created: {arguments.output}")


def format_cli_command(args, detected_params=None) -> str:
    """Format the command line arguments for reuse."""
    cmd: list[str] = ["rssfixer"]

    # Add the detected method flag
    if args.html:
        cmd.append("--html")
    elif args.json:
        cmd.append("--json")
    elif args.list:
        cmd.append("--list")
    elif args.release:
        cmd.append("--release")

    # Add all relevant parameters
    params_to_include = [
        # HTML params
        ("html_entries", "--html-entries"),
        ("html_entries_class", "--html-entries-class"),
        ("html_url", "--html-url"),
        ("html_title", "--html-title"),
        ("html_title_class", "--html-title-class"),
        ("html_description", "--html-description"),
        ("html_description_class", "--html-description-class"),
        # JSON params
        ("json_entries", "--json-entries"),
        ("json_url", "--json-url"),
        ("json_title", "--json-title"),
        ("json_description", "--json-description"),
        # Release params
        ("release_url", "--release-url"),
        ("release_entries", "--release-entries"),
        # Filter params
        ("filter_type", "--filter-type"),
        ("filter_name", "--filter-name"),
        ("title_filter", "--title-filter"),
        # Other params - we'll handle base_url separately
    ]

    # Add detected parameters
    for param_name, flag in params_to_include:
        value = None
        # Check detected params first (if provided)
        if detected_params and param_name in detected_params:
            value = detected_params[param_name]
        # Otherwise check args
        elif hasattr(args, param_name) and getattr(args, param_name):
            value = getattr(args, param_name)

        if value:
            cmd.append(flag)
            cmd.append(f'"{value}"')

    # Add the title if specified
    if args.title and args.title != f"RSS Feed for {args.url}":
        cmd.append(f'--title "{args.title}"')

    # Add other simple flags
    if args.atom:
        cmd.append("--atom")

    # Add the URL at the end
    cmd.append(args.url)

    return " ".join(cmd)


def print_preview(links, detection_result, args):  # noqa: PLR0912
    """Print a preview of the feed and the detected settings."""
    print("\n=== Feed Preview ===")
    print(f"Extraction method: {detection_result.get('method', 'Unknown')}")

    # Print the first 3 titles (or fewer if less available)
    preview_count = min(3, len(links))

    # Check if we need base_url for relative URLs
    needs_base_url = False
    for i in range(min(len(links), 10)):  # Check first 10 links
        url, _, _ = links[i]
        if not url.startswith(("http://", "https://")):
            needs_base_url = True
            break

    # Add base URL suggestion if needed
    if needs_base_url and not args.base_url:
        base_url = args.url
        if not base_url.endswith("/"):
            # Extract domain part
            from urllib.parse import urlparse

            parsed_url = urlparse(base_url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            print(f'\nWARNING: Relative URLs detected. Consider adding --base-url "{domain}"')
        else:
            print(f'\nWARNING: Relative URLs detected. Consider adding --base-url "{base_url}"')

    for i in range(preview_count):
        url, title, description = links[i]
        print(f"{i+1}. {title}")
        if args.debug:
            if not url.startswith(("http://", "https://")) and args.base_url:
                full_url = args.base_url + url
                print(f"   URL: {url} -> {full_url}")
            else:
                print(f"   URL: {url}")
            if description:
                print(f"   Description: {description[:50]}...")

    # Print total number of entries
    print(f"\nTotal entries found: {len(links)}")

    # Print command to reproduce
    print("\n=== Command to reproduce this feed ===")
    command = format_cli_command(args, detection_result)

    # Add base-url to command if needed and not already present
    if needs_base_url and not args.base_url:
        base_url = args.url
        if not base_url.endswith("/"):
            from urllib.parse import urlparse

            parsed_url = urlparse(base_url)
            domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            command = command.replace(args.url, f'--base-url "{domain}" {args.url}')
        else:
            command = command.replace(args.url, f'--base-url "{base_url}" {args.url}')

    print(command)
    print("\n")


def main(args=None):  # noqa: PLR0912, PLR0915
    """Handle program arguments."""
    if args is None:
        args = sys.argv[1:]

    args = parse_arguments(arguments=args)

    # Track if auto-detection was used
    auto_detection_used = False
    detection_result = None

    # Get HTML content from URL
    html_content: str = fetch_html(arguments=args)
    soup = BeautifulSoup(markup=html_content, features="html.parser")

    # Extract page title if not specified
    if not args.title:
        title_tag = soup.find(name="title")
        if title_tag:
            args.title = title_tag.text.strip()
        else:
            args.title = "RSS Feed for " + args.url

    # Filter web page if requested
    if args.filter_type and args.filter_name:
        soup: BeautifulSoup = filter_html(soup=soup, filter_type=args.filter_type, filter_name=args.filter_name)

    # Auto-detect extraction method if not explicitly specified
    if args.auto and not (args.html or args.json or args.list or args.release):
        if args.debug:
            print("DEBUG: Auto-detecting extraction method...")

        detection_result = detect_extraction_method(soup=soup, url=args.url)
        auto_detection_used = True

        if detection_result:
            method = detection_result.pop("method")
            if args.debug:
                print(f"DEBUG: Detected method: {method}")
                print(f"DEBUG: Detected parameters: {detection_result}")

            # Set the detected method flag
            setattr(args, method, True)

            # Apply detected parameters
            for key, value in detection_result.items():
                if not getattr(args, key, None):  # Only set if not explicitly provided
                    setattr(args, key, value)
        else:
            if not args.quiet:
                print("WARNING: Could not auto-detect extraction method, falling back to list mode")
            args.list = True
            detection_result = {"method": "list"}

    if args.debug:
        print("DEBUG: Using extraction method:")
        if args.json:
            print("DEBUG: JSON mode")
        elif args.html:
            print("DEBUG: HTML mode")
        elif args.release:
            print("DEBUG: Release mode")
        else:
            print("DEBUG: List mode")

    # Select function to handle different types of blogs
    if args.json:
        links = extract_links_json(soup=soup, arguments=args)
    elif args.html:
        links = extract_links_html(soup=soup, arguments=args)
    elif args.release:
        if not getattr(args, "release_url", None):
            print("ERROR: Release URL not specified")
            sys.exit(1)
        links = extract_links_release(soup=soup, arguments=args)
    else:  # Default to list mode
        links = extract_links_ul(soup=soup)

    # When auto-detection was used, show a preview before creating the feed
    if auto_detection_used and not args.quiet:
        if detection_result is None:
            detection_result = {"method": "list" if args.list else "unknown"}
        print_preview(links=links, detection_result=detection_result, args=args)

        # If only the preview is needed (no output file), exit here
        if args.stdout and not args.quiet:
            return

    # Create RSS feed and save to file
    rss_feed = create_rss_feed(links=links, arguments=args)
    if args.stdout:
        print(rss_feed)
    else:
        save_rss_feed(rss_feed=rss_feed, arguments=args)


def init() -> None:
    """Initialize the script."""
    if __name__ == "__main__":
        sys.exit(main())


init()
