"""RSS/Atom feed generation functionality."""

from typing import Any

from feedgen.feed import FeedGenerator

from .models import LinkEntry


def create_rss_feed(links: list[LinkEntry], arguments: Any) -> str:
    """Create an RSS or Atom feed from a list of links.
    
    Args:
        links: List of LinkEntry objects
        arguments: Parsed command line arguments
        
    Returns:
        RSS or Atom feed as string

    """
    feed_description = f"RSS feed generated from the links at {arguments.url}"

    # Create the feed generator
    fg = FeedGenerator()
    fg.id(arguments.url)
    fg.title(arguments.title)
    fg.description(feed_description)
    fg.link(href=arguments.url, rel="alternate")

    # Add entries to the feed
    for link_entry in links:
        fe = fg.add_entry()

        # Build full URL if base_url is provided
        feed_url = link_entry.url
        if arguments.base_url and not link_entry.url.startswith("http"):
            feed_url = arguments.base_url + link_entry.url

        fe.link(href=feed_url)
        fe.id(feed_url)
        fe.title(link_entry.title)

        # Handle Atom vs RSS format differences
        if getattr(arguments, "atom", False):
            fe.summary(link_entry.description)
            fe.content(content=link_entry.description, src=link_entry.url)
        else:
            fe.description(link_entry.description)

    # Generate appropriate feed format
    if getattr(arguments, "atom", False):
        return fg.atom_str(pretty=True).decode("utf-8")
    return fg.rss_str(pretty=True).decode("utf-8")
