"""Tests for rss.py."""
import json

import rssfixer.rss as rss


json_string = {
    "foo": "bar",
    "baz": {
        "qux": "battery",
        "horse": "stable",
    },
    "home": {
        "waldo": "fred",
        "away": "xyzzy",
        "thud": "thud",
    },
}

html = """
<html>
    <head>
        <title>Test</title>
    </head>
    <body>
        <ul>
            <li><a href="https://example.com/1">Example 1</a></li>
            <li><a href="https://example.com/2">Example 2</a></li>
            <li><a href="https://example.com/3">Example 3</a></li>
        </ul>
    </body>
</html>
"""

def test_find_entries():
    """Test find_entries()."""

    json_object = json.loads(json.dumps(json_string))

    entries = rss.find_entries(json_object, "home")
    assert entries == {
        "waldo": "fred",
        "away": "xyzzy",
        "thud": "thud",
    }

def test_find_entries_not_found():
    """Test find_entries() when the entry is not found."""

    json_object = json.loads(json.dumps(json_string))

    entries = rss.find_entries(json_object, "xyzzy")
    assert entries is None


def test_extract_links_ul():
    """Test extract_links_html()."""
   
    soup = rss.BeautifulSoup(html, "html.parser")
    links = rss.extract_links_ul(soup)
    assert links == [
        ("https://example.com/1", "Example 1", "Example 1"),
        ("https://example.com/2", "Example 2", "Example 2"),
        ("https://example.com/3", "Example 3", "Example 3"),
    ]


def test_extract_links_html_ignore():
    """Test that extract_links_html() excludes author and category."""

    soup = rss.BeautifulSoup(html, "html.parser")
    links = rss.extract_links_ul(soup)
    assert links == [
        ("https://example.com/1", "Example 1", "Example 1"),
        ("https://example.com/2", "Example 2", "Example 2"),
        ("https://example.com/3", "Example 3", "Example 3"),
    ]
