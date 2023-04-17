"""Generate rss feed from "blogs" without rss feed."""
import argparse
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import json
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

def extract_links(soup):
    """Extract links from an HTML page with links in <ul>-lists."""
    links = []
    unique_links = set()

    # Iterate through all the <ul> elements in the page
    for links_list in soup.find_all('ul', class_=None):
        for li in links_list.find_all('li'):
            link = li.find('a')
            if link:
                url = link['href']
                title = link.text.strip()
                description = link.text.strip()

                # Exclude URLs containing '/category/' or '/author/'
                if '/category/' not in url and '/author/' not in url:
                    # Check if the URL is unique
                    if url not in unique_links:
                        unique_links.add(url)
                        links.append((url, title, description))

    if links == []:
        print("ERROR: No links found")
        sys.exit(1)
    return links

def extract_links_json(soup, arguments):
    """Extract links from JSON strings in an HTML page."""
    links = []
    unique_links = set()

    # Find the JSON string in the page
    for json_text in soup.find_all('script', type="application/json"):
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

def create_rss_feed(links, html_url, feed_title, feed_description):
    """Create an RSS feed from a list of links."""
    fg = FeedGenerator()
    fg.id(html_url)
    fg.title(feed_title)
    fg.description(feed_description)
    fg.link(href=html_url, rel="alternate")

    for url, title, description in links:
        fe = fg.add_entry()
        fe.id(url)
        fe.title(title)
        fe.link(href=url)
        fe.description(description)

    return fg.rss_str(pretty=True).decode("utf-8")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate RSS feed for blog that don't publish a feed")
    parser.add_argument("url", help="URL for the blog")
    parser.add_argument("--json", action="store_true", help="Find entries in JSON")
    parser.add_argument("--json-entries", default="entries", help="JSON key for entries (default: 'entries')")
    parser.add_argument("--json-url", default="url", help="JSON key for URL (default: 'url')")
    parser.add_argument("--json-title", default="title", help="JSON key for title (default: 'title')")
    parser.add_argument("--json-description", default="preamble", help="JSON key for description (default: 'preamble')")
    parser.add_argument("--output", default="rss_feed.xml", help='Name of the output file (default: "rss_feed.xml")')
    parser.add_argument("--title", default="My RSS Feed", help='Title of the RSS feed (default: "My RSS Feed")')
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress output")
    args = parser.parse_args()

    html_content = fetch_html(args.url)
    soup = BeautifulSoup(html_content, "html.parser")
    if args.json:
        links = extract_links_json(soup, args)
    else:
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
