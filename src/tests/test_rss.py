"""Tests for rss.py."""
import pickle
import re

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


def test_fetch_html(requests_mock):
    """Test the fetch_html function."""
    url = "https://research.nccgroup.com/"
    with open("src/tests/data/input/nccgroup.html", "r", encoding="utf-8") as f:
        content = f.read()
    requests_mock.get(url, text=content)
    assert content == rss.fetch_html(url)


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


def test_extract_links_ul_simple(example_html_string):
    """Test extract_links_html()."""
    soup = BeautifulSoup(example_html_string, "html.parser")
    links = rss.extract_links_ul(soup)
    assert links == [
        ("https://example.com/1", "Example 1", "Example 1"),
        ("https://example.com/2", "Example 2", "Example 2"),
        ("https://example.com/3", "Example 3", "Example 3"),
    ]


def test_extract_links_ul_standard():
    """Test extract_links_html()."""
    with open("src/tests/data/input/nccgroup.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    links = rss.extract_links_ul(soup)
    with open("src/tests/data/output/nccgroup", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_html():
    """Test extract_links_html()."""
    with open("src/tests/data/input/tripwire.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        ["--html", "http://www.tripwire.com/state-of-security"]
    )
    links = rss.extract_links_html(soup, arguments)
    with open("src/tests/data/output/tripwire", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_json():
    """Test extract_links_json()."""
    with open("src/tests/data/input/truesec.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(["--json", "https://www.truesec.com/hub/blog"])
    links = rss.extract_links_json(soup, arguments)
    with open("src/tests/data/output/truesec", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_create_rss_feed():
    """Test create_rss_feed()."""
    with open("src/tests/data/output/nccgroup", "rb") as f:
        links = pickle.load(f)
    with open("src/tests/data/output/nccgroup.xml", "r", encoding="utf-8") as f:
        correct_rss_feed = f.read()
    arguments = rss.parse_arguments(
        ["--title", "nccgroup", "--list", "https://research.nccgroup.com/"]
    )
    rss_feed = rss.create_rss_feed(links, arguments)
    rss_feed = re.sub(
        r"<lastBuildDate>.*</lastBuildDate>",
        "<lastBuildDate>Fri, 21 Apr 2023 12:15:48 +0000</lastBuildDate>",
        rss_feed,
    )
    assert rss_feed == correct_rss_feed
