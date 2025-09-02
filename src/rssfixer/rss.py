"""Generate rss feed for "blogs" without rss feed."""

import sys

from bs4 import BeautifulSoup

from .cli import get_extractor, parse_arguments
from .exceptions import RSSFixerError
from .feed import create_rss_feed
from .utils import fetch_html, filter_html, save_rss_feed


def main(args=None):
    """Handle program arguments."""
    if args is None:
        args = sys.argv[1:]

    try:
        args = parse_arguments(args)

        # Get HTML content from URL
        headers = {"User-Agent": args.user_agent}
        html_content = fetch_html(args.url, headers)
        soup = BeautifulSoup(html_content, "html.parser")

        # Filter web page if specified
        if args.filter_type and args.filter_name:
            soup = filter_html(soup, args.filter_type, args.filter_name)

        if args.debug:
            print("DEBUG: Filtered HTML\n")
            print(soup.prettify())

        # Get appropriate extractor and extract links
        extractor = get_extractor(args)
        links = extractor.extract_links(soup)

        # Create RSS feed and save to file
        rss_feed = create_rss_feed(links, args)
        if args.stdout:
            print(rss_feed)
        else:
            save_rss_feed(rss_feed, args.output, getattr(args, "atom", False), args.quiet)

    except RSSFixerError as e:
        print(f"ERROR: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"UNEXPECTED ERROR: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
