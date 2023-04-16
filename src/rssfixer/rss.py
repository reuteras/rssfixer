"""Generate rss feed from "blogs" without rss feed."""
import argparse
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests
import sys

def fetch_html(url):
    """Fetch HTML content from a URL."""
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out")
        sys.exit(1)
    return response.text

def extract_links(soup):
    """Extract links from an HTML page."""
    links = []
    unique_links = set()

    # Iterate through all the <ul> elements in the page
    for links_list in soup.find_all('ul', class_=None):
        for li in links_list.find_all('li'):
            link = li.find('a')
            if link:
                url = link['href']
                title = link.text.strip()

                # Exclude URLs containing '/category/' or '/author/'
                if '/category/' not in url and '/author/' not in url:
                    # Check if the URL is unique
                    if url not in unique_links:
                        unique_links.add(url)
                        links.append((url, title))

    if links == []:
        print("ERROR: No links found")
        sys.exit(1)
    return links

def create_rss_feed(links, html_url, feed_title, feed_description):
    """Create an RSS feed from a list of links."""
    fg = FeedGenerator()
    fg.id(html_url)
    fg.title(feed_title)
    fg.description(feed_description)
    fg.link(href=html_url, rel="alternate")

    for url, title in links:
        fe = fg.add_entry()
        fe.id(url)
        fe.title(title)
        fe.link(href=url)

    return fg.rss_str(pretty=True).decode("utf-8")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Convert an HTML list of links to an RSS feed")
    parser.add_argument("url", help="URL of the HTML list of links")
    parser.add_argument("--title", default="My RSS Feed", help='Title of the RSS feed (default: "My RSS Feed")')
    parser.add_argument("--output", default="rss_feed.xml", help='Name of the output file (default: "rss_feed.xml")')
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    html_content = fetch_html(args.url)
    soup = BeautifulSoup(html_content, "html.parser")
    links = extract_links(soup)
    feed_description = f"RSS feed generated from the links at {args.url}"
    rss_feed = create_rss_feed(links, args.url, args.title, feed_description)

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(rss_feed)
    except IOError:
        print("ERROR: Unable to write to file")
        sys.exit(1)

    if not args.quiet:
        print(f"RSS feed created: {args.output}")

if __name__ == "__main__":
    main()
