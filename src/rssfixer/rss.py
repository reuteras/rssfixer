"""Generate rss feed for "blogs" without rss feed."""
import argparse
import json
import re
import sys

import pkg_resources
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator


def fetch_html(url):
    """Fetch HTML content from a URL."""
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out")
        sys.exit(1)
    return response.text


def find_entries(json_object, entries_key):
    """Find the entries in a JSON object with key "entries_key"."""
    if isinstance(json_object, dict):
        for key, value in json_object.items():
            if key == entries_key:
                return value
            else:
                result = find_entries(value, entries_key)
                if result is not None:
                    return result
    elif isinstance(json_object, list):
        for item in json_object:
            result = find_entries(item, entries_key)
            if result is not None:
                return result
    return None


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


def extract_links_html(soup, arguments):
    """Extract links from an HTML page with links in selectable elements."""
    links = []
    unique_links = set()

    # Iterate through all the elements of type html_entries in the page
    for entry in soup.find_all(arguments.html_entries):
        try:
            url = entry.findNext(arguments.html_url)["href"]
            title = entry.find(
                arguments.html_title, re.compile(arguments.html_title_class)
            ).text.strip()
        except (KeyError, AttributeError):
            print("ERROR: Unable to find URL or title in HTML element")
            sys.exit(1)
        try:
            description = entry.find(
                arguments.html_description, re.compile(arguments.html_description_class)
            ).text.strip()
        except (KeyError, AttributeError):
            # Ignore description if it's not found
            description = ""
        if url not in unique_links:
            unique_links.add(url)
            links.append((url, title, description))

    if not links:
        print("ERROR: No links found")
        sys.exit(1)
    return links


def extract_links_json(soup, arguments):
    """Extract links from JSON strings in an HTML page."""
    links = []
    unique_links = set()

    # Find the JSON string in the page
    for json_text in soup.find_all("script", type="application/json"):
        json_object = json.loads(json_text.text)
        entries = find_entries(json_object, arguments.json_entries)
        if entries is not None:
            break

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

    if links == []:
        print("ERROR: No links found")
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
        if arguments.base_url:
            url = arguments.base_url + url
        fe = fg.add_entry()
        fe.id(url)
        fe.title(title)
        fe.link(href=url)
        fe.description(description)

    if vars(arguments).get("atom", False):
        return fg.atom_str(pretty=True).decode("utf-8")
    else:
        return fg.rss_str(pretty=True).decode("utf-8")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="""Generate RSS feed for blog that don't publish a feed.
        Default is to find links in a simple <ul>-list.
        Options are available to find links in other HTML elements or JSON strings."""
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + pkg_resources.get_distribution("rssfixer").version,
    )
    parser.add_argument("url", help="URL for the blog")
    parser.add_argument("--atom", action="store_true", help="Generate Atom feed")
    parser.add_argument("--base-url", help="Base URL for the blog")
    parser.add_argument("--html", action="store_true", help="Find entries in HTML")
    parser.add_argument(
        "--html-entries", default="article", help="HTML selector for entries"
    )
    parser.add_argument("--html-url", default="a", help="HTML selector for URL")
    parser.add_argument("--html-title", default="h3", help="HTML selector for title")
    parser.add_argument(
        "--html-title-class",
        default="title",
        help="Flag to specify title class (regex)",
    )
    parser.add_argument(
        "--html-description",
        default="div",
        help="HTML selector for description",
    )
    parser.add_argument(
        "--html-description-class",
        default="summary",
        help="Flag to specify description class (regex)",
    )
    parser.add_argument("--json", action="store_true", help="Find entries in JSON")
    parser.add_argument(
        "--json-entries",
        default="entries",
        help="JSON key for entries (default: 'entries')",
    )
    parser.add_argument(
        "--json-url", default="url", help="JSON key for URL (default: 'url')"
    )
    parser.add_argument(
        "--json-title",
        default="title",
        help="JSON key for title",
    )
    parser.add_argument(
        "--json-description",
        default="preamble",
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
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    parser.add_argument(
        "--list", action="store_true", help="Find entries in HTML <ul>-list (default)"
    )

    return parser


def save_rss_feed(rss_feed, arguments):
    """Save the RSS feed to a file."""
    try:
        with open(arguments.output, "w", encoding="utf-8") as f:
            f.write(rss_feed)
    except IOError:
        print("ERROR: Unable to write to file")
        sys.exit(1)

    if not arguments.quiet:
        if arguments.atom:
            print(f"Atom feed created: {arguments.output}")
        else:
            print(f"RSS feed created: {arguments.output}")


def main():
    """Main function."""
    parsed_args = parse_arguments()
    args = parsed_args.parse_args()

    if vars(args).get("version"):
        print(pkg_resources.require("rssfixer")[0].version)
        sys.exit(0)

    # Get HTML content from URL
    html_content = fetch_html(args.url)
    soup = BeautifulSoup(html_content, "html.parser")

    # Select function to handle different types of blogs
    if args.json:
        links = extract_links_json(soup, args)
    elif args.html:
        links = extract_links_html(soup, args)
    elif args.list:
        links = extract_links_ul(soup)
    else:
        links = extract_links_ul(soup)

    # Create RSS feed and save to file
    rss_feed = create_rss_feed(links, args)
    save_rss_feed(rss_feed, args)


if __name__ == "__main__":
    main()
