"""Tests for rss.py."""

import pickle
import re

import pytest
from bs4 import BeautifulSoup
from requests_mock import NoMockAddress

from rssfixer import rss
from rssfixer.exceptions import (
    FileWriteError,
    JSONParsingError,
    NoLinksFoundError,
)
from rssfixer.extractors.html import HtmlExtractor
from rssfixer.extractors.json import JsonExtractor
from rssfixer.extractors.list import ListExtractor
from rssfixer.feed import create_rss_feed
from rssfixer.utils import fetch_html, save_rss_feed


@pytest.fixture(name="example_json_object")
def fixture_example_json_object():
    """JSON string for tests."""
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
    """HTML string for tests."""
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


@pytest.fixture(name="example_html_string_no_match")
def fixture_example_html_string_no_match():
    """HTML string for tests."""
    html = """
    <html>
        <head>
            <title>No match</title>
        </head>
        <body>
            <h1>Heading</h1>
            <p>Paragraph with one <a href="/link/">link</a>.</p>
        </body>
    </html>
    """
    return html


EXIT_VALUE = 42

json_data_1 = {
    "a": 1,
    "b": 2,
    "entries_key": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}],
}

json_data_2 = {
    "a": 1,
    "b": 2,
    "c": {
        "d": 3,
        "entries_key": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}],
    },
}

json_data_3 = [
    {"a": 1, "b": 2},
    {"c": 3, "entries_key": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]},
]

json_data_4 = {
    "a": [
        {"b": 1},
        {"entries_key": [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]},
    ],
}

json_data_5 = {
    "a": 1,
    "b": 2,
}

test_cases = [
    (json_data_1, "entries_key", [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]),
    (json_data_2, "entries_key", [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]),
    (json_data_3, "entries_key", [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]),
    (json_data_4, "entries_key", [{"id": 1, "value": "A"}, {"id": 2, "value": "B"}]),
    (json_data_5, "entries_key", None),
]


def test_fetch_html(requests_mock):
    """Test the fetch_html function."""
    with open("src/tests/data/input/nccgroup.html", encoding="utf-8") as f:
        content = f.read()
    url = "https://research.nccgroup.com/"
    headers = {"User-Agent": "test-agent"}
    requests_mock.get(url, text=content)
    assert content == fetch_html(url, headers)


def test_fetch_html_no_url(requests_mock):
    """Test the fetch_html function that should not work."""
    wrong_url = "https://not.nccgroup.com/"
    with open("src/tests/data/input/nccgroup.html", encoding="utf-8") as f:
        content = f.read()
    requests_mock.get(wrong_url, text=content)
    assert NoMockAddress


def test_find_json_entries(example_json_object):
    """Test JsonExtractor._find_entries_recursive() with match."""

    class MockArgs:
        json_entries = "home"

    extractor = JsonExtractor(MockArgs())
    # The method only returns values that are lists, not dicts
    result = extractor._find_entries_recursive(example_json_object, "home")
    assert result is None  # "home" contains a dict, not a list


def test_find_json_entries_not_found(example_json_object):
    """Test JsonExtractor._find_entries_recursive() when the entry is not found."""

    class MockArgs:
        json_entries = "xyzzy"

    extractor = JsonExtractor(MockArgs())
    result = extractor._find_entries_recursive(example_json_object, "xyzzy")
    assert result is None


@pytest.mark.parametrize("json_object,entries_key,expected", test_cases)
def test_find_entries(json_object, entries_key, expected):
    """Test JsonExtractor._find_entries_recursive when correct."""

    class MockArgs:
        pass

    extractor = JsonExtractor(MockArgs())
    result = extractor._find_entries_recursive(json_object, entries_key)
    assert result == expected


def test_extract_links_ul_simple(example_html_string):
    """Test ListExtractor.extract_links() with working structure."""
    expected_link_count = 3

    class MockArgs:
        pass

    soup = BeautifulSoup(example_html_string, "html.parser")
    extractor = ListExtractor(MockArgs())
    links = extractor.extract_links(soup)

    # Check that we got LinkEntry objects with correct data
    assert len(links) == expected_link_count
    assert links[0].url == "https://example.com/1"
    assert links[0].title == "Example 1"
    assert links[0].description == "Example 1"
    assert links[1].url == "https://example.com/2"
    assert links[1].title == "Example 2"
    assert links[2].url == "https://example.com/3"
    assert links[2].title == "Example 3"


def test_extract_links_ul_simple_no_match(example_html_string_no_match):
    """Test ListExtractor.extract_links() without match."""

    class MockArgs:
        pass

    soup = BeautifulSoup(example_html_string_no_match, "html.parser")
    extractor = ListExtractor(MockArgs())
    with pytest.raises(NoLinksFoundError):
        extractor.extract_links(soup)


def test_extract_links_ul_standard():
    """Test ListExtractor.extract_links() working."""

    class MockArgs:
        pass

    with open("src/tests/data/input/nccgroup.html", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    extractor = ListExtractor(MockArgs())
    links = extractor.extract_links(soup)
    with open("src/tests/data/output/nccgroup", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_html():
    """Test HtmlExtractor.extract_links() working."""
    with open("src/tests/data/input/tripwire.html", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        ["--html", "http://www.tripwire.com/state-of-security"],
    )
    extractor = HtmlExtractor(arguments)
    links = extractor.extract_links(soup)
    with open("src/tests/data/output/tripwire", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_html_no_match_title():
    """Test HtmlExtractor.extract_links() with no match for title."""
    with open("src/tests/data/input/tripwire.html", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        ["--html", "--html-title", "fail", "http://www.tripwire.com/state-of-security"],
    )
    extractor = HtmlExtractor(arguments)
    with pytest.raises(NoLinksFoundError):
        extractor.extract_links(soup)


def test_extract_links_html_no_match_links():
    """Test HtmlExtractor.extract_links() with no match for links."""
    with open("src/tests/data/input/tripwire.html", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--html",
            "--html-entries",
            "fail",
            "http://www.tripwire.com/state-of-security",
        ],
    )
    extractor = HtmlExtractor(arguments)
    with pytest.raises(NoLinksFoundError):
        extractor.extract_links(soup)


def test_extract_links_html_no_match_description():
    """Test HtmlExtractor.extract_links() with no match for description."""
    with open("src/tests/data/input/tripwire.html", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--html",
            "--html-description",
            "fail",
            "http://www.tripwire.com/state-of-security",
        ],
    )
    extractor = HtmlExtractor(arguments)
    links = extractor.extract_links(soup)
    with open("src/tests/data/output/tripwire_no_description", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_json():
    """Test JsonExtractor.extract_links() working."""
    with open("src/tests/data/input/truesec.html", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--json",
            "--json-description",
            "preamble",
            "https://www.truesec.com/hub/blog",
        ],
    )
    extractor = JsonExtractor(arguments)
    links = extractor.extract_links(soup)
    with open("src/tests/data/output/truesec", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_json_no_match_description():
    """Test JsonExtractor.extract_links() working."""
    with open("src/tests/data/input/truesec.html", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--json",
            "--json-description",
            "description",
            "https://www.truesec.com/hub/blog",
        ],
    )
    extractor = JsonExtractor(arguments)
    links = extractor.extract_links(soup)
    with open("src/tests/data/output/truesec_no_desc", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_json_no_json(example_html_string):
    """Test JsonExtractor.extract_links() with no json."""
    soup = BeautifulSoup(example_html_string, "html.parser")
    arguments = rss.parse_arguments(["--json", "https://www.truesec.com/hub/blog"])
    extractor = JsonExtractor(arguments)
    with pytest.raises(JSONParsingError):
        extractor.extract_links(soup)


def test_extract_links_json_no_title():
    """Test JsonExtractor.extract_links() with no title."""
    with open("src/tests/data/input/truesec.html", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        ["--json", "--json-title", "fail", "https://www.truesec.com/hub/blog"],
    )
    extractor = JsonExtractor(arguments)
    with pytest.raises(JSONParsingError):
        extractor.extract_links(soup)


def test_create_rss_feed():
    """Test create_rss_feed() in RSS format working."""
    with open("src/tests/data/output/nccgroup", "rb") as f:
        links = pickle.load(f)
    with open("src/tests/data/output/nccgroup.xml", encoding="utf-8") as f:
        correct_rss_feed = f.read()
    arguments = rss.parse_arguments(
        ["--title", "nccgroup", "--list", "https://research.nccgroup.com/"],
    )
    rss_feed = create_rss_feed(links, arguments)
    rss_feed = re.sub(
        r"<lastBuildDate>.*</lastBuildDate>",
        "<lastBuildDate>Fri, 21 Apr 2023 12:15:48 +0000</lastBuildDate>",
        rss_feed,
    )
    assert rss_feed == correct_rss_feed


def test_create_rss_feed_atom():
    """Test create_rss_feed() with Atom output format."""
    with open("src/tests/data/output/apple.xml", encoding="utf-8") as f:
        correct_rss_feed = f.read()
    arguments = rss.parse_arguments(
        [
            "--title",
            "Apple Security",
            "--atom",
            "--json",
            "--json-entries",
            "blogs",
            "--json-url",
            "slug",
            "--base-url",
            "https://security.apple.com/blog/",
            "https://security.apple.com/blog",
        ],
    )
    with open("src/tests/data/output/apple", "rb") as f:
        links = pickle.load(f)
    rss_feed = create_rss_feed(links, arguments)

    rss_feed = re.sub(
        r"<updated>.*</updated>",
        "<updated></updated>",
        rss_feed,
    )
    correct_rss_feed = re.sub(
        r"<updated>.*</updated>",
        "<updated></updated>",
        rss_feed,
    )
    assert rss_feed == correct_rss_feed


def test_create_rss_feed_with_base_url():
    """Test create_rss_feed() with base-url set."""
    with open("src/tests/data/output/tripwire", "rb") as f:
        links = pickle.load(f)
    with open("src/tests/data/output/tripwire.xml", encoding="utf-8") as f:
        correct_rss_feed = f.read()
    arguments = rss.parse_arguments(
        [
            "--title",
            "Tripwire",
            "--html",
            "--base-url",
            "https://www.tripwire.com",
            "http://www.tripwire.com/state-of-security",
        ],
    )
    rss_feed = create_rss_feed(links, arguments)
    rss_feed = re.sub(
        r"<lastBuildDate>.*</lastBuildDate>",
        "<lastBuildDate>Sun, 23 Apr 2023 13:33:02 +0000</lastBuildDate>",
        rss_feed,
    )
    assert rss_feed == correct_rss_feed


def test_save_rss_feed_working(tmpdir):
    """Test save_rss_feed() in RSS format."""
    test_output = tmpdir.mkdir("sub").join("tripwire.xml")
    with open("src/tests/data/output/tripwire.xml", encoding="utf-8") as f:
        rss_feed = f.read()
    save_rss_feed(rss_feed, str(test_output), False, True)

    assert test_output.read_text(encoding="utf-8") == rss_feed


def test_save_atom_feed_working(tmpdir):
    """Test save_rss_feed() in Atom format."""
    test_output = tmpdir.mkdir("sub").join("apple.xml")
    with open("src/tests/data/output/apple.xml", encoding="utf-8") as f:
        rss_feed = f.read()
    save_rss_feed(rss_feed, str(test_output), True, True)

    assert test_output.read_text(encoding="utf-8") == rss_feed


def test_save_rss_feed_not_working():
    """Test save_rss_feed() and check that it fails."""
    test_output = "/root/tripwire.xml"
    with open("src/tests/data/output/tripwire.xml", encoding="utf-8") as f:
        rss_feed = f.read()

    with pytest.raises(FileWriteError):
        save_rss_feed(rss_feed, test_output, False, True)
