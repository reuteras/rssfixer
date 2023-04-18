"""Tests for rss.py."""
import pytest
import rssfixer.rss as rss
from bs4 import BeautifulSoup


@pytest.fixture(name="example_json_object")
def fixture_example_json_object():
    """Example JSON string."""
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
    return json_string


@pytest.fixture(name="example_html_string")
def fixture_example_html_string():
    """Example HTML string."""
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
    return html


def test_find_entries(example_json_object):
    """Test find_entries()."""
    json_object = example_json_object
    entries = rss.find_entries(json_object, "home")
    assert entries == {
        "waldo": "fred",
        "away": "xyzzy",
        "thud": "thud",
    }


def test_find_entries_not_found(example_json_object):
    """Test find_entries() when the entry is not found."""
    json_object = example_json_object
    entries = rss.find_entries(json_object, "xyzzy")
    assert entries is None


def test_extract_links_ul(example_html_string):
    """Test extract_links_html()."""
    soup = BeautifulSoup(example_html_string, "html.parser")
    links = rss.extract_links_ul(soup)
    assert links == [
        ("https://example.com/1", "Example 1", "Example 1"),
        ("https://example.com/2", "Example 2", "Example 2"),
        ("https://example.com/3", "Example 3", "Example 3"),
    ]


def test_extract_links_html_ignore(example_html_string):
    """Test that extract_links_html() excludes author and category."""
    soup = BeautifulSoup(example_html_string, "html.parser")
    links = rss.extract_links_ul(soup)
    assert links == [
        ("https://example.com/1", "Example 1", "Example 1"),
        ("https://example.com/2", "Example 2", "Example 2"),
        ("https://example.com/3", "Example 3", "Example 3"),
    ]
