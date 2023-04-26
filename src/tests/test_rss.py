"""Tests for rss.py."""
import pickle
import re
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from requests_mock import NoMockAddress
from rssfixer import rss


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


@pytest.fixture(name="example_html_string_no_match")
def fixture_example_html_string_no_match():
    """Example HTML string without list."""
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
    ]
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
    url = "https://research.nccgroup.com/"
    with open("src/tests/data/input/nccgroup.html", "r", encoding="utf-8") as f:
        content = f.read()
    requests_mock.get(url, text=content)
    assert content == rss.fetch_html(url)


def test_fetch_html_no_url(requests_mock):
    """Test the fetch_html function that should not work."""
    wrong_url = "https://not.nccgroup.com/"
    with open("src/tests/data/input/nccgroup.html", "r", encoding="utf-8") as f:
        content = f.read()
    requests_mock.get(wrong_url, text=content)
    assert NoMockAddress


def test_find_json_entries(example_json_object):
    """Test find_entries() with match."""
    json_object = example_json_object
    entries = rss.find_entries(json_object, "home")
    assert entries == {
        "waldo": "fred",
        "away": "xyzzy",
        "thud": "thud",
    }


def test_find_json_entries_not_found(example_json_object):
    """Test find_entries() when the entry is not found."""
    json_object = example_json_object
    entries = rss.find_entries(json_object, "xyzzy")
    assert entries is None


@pytest.mark.parametrize("json_object,entries_key,expected", test_cases)
def test_find_entries(json_object, entries_key, expected):
    result = rss.find_entries(json_object, entries_key)
    assert result == expected


def test_extract_links_ul_simple(example_html_string):
    """Test extract_links_html() with working structure."""
    soup = BeautifulSoup(example_html_string, "html.parser")
    links = rss.extract_links_ul(soup)
    assert links == [
        ("https://example.com/1", "Example 1", "Example 1"),
        ("https://example.com/2", "Example 2", "Example 2"),
        ("https://example.com/3", "Example 3", "Example 3"),
    ]


def test_extract_links_ul_simple_no_match(example_html_string_no_match):
    """Test extract_links_html() without match."""
    soup = BeautifulSoup(example_html_string_no_match, "html.parser")
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.extract_links_ul(soup)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_extract_links_ul_standard():
    """Test extract_links_html() working."""
    with open("src/tests/data/input/nccgroup.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    links = rss.extract_links_ul(soup)
    with open("src/tests/data/output/nccgroup", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_html():
    """Test extract_links_html() working."""
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


def test_extract_links_html_no_match_title():
    """Test extract_links_html() with no match for title."""
    with open("src/tests/data/input/tripwire.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        ["--html", "--html-title", "fail", "http://www.tripwire.com/state-of-security"]
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.extract_links_html(soup, arguments)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_extract_links_html_no_match_links():
    """Test extract_links_html() with no match for links."""
    with open("src/tests/data/input/tripwire.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--html",
            "--html-entries",
            "fail",
            "http://www.tripwire.com/state-of-security",
        ]
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.extract_links_html(soup, arguments)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_extract_links_html_no_match_description():
    """Test extract_links_html() with no match for description."""
    with open("src/tests/data/input/tripwire.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--html",
            "--html-description",
            "fail",
            "http://www.tripwire.com/state-of-security",
        ]
    )
    links = rss.extract_links_html(soup, arguments)
    with open("src/tests/data/output/tripwire_no_description", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_json():
    """Test extract_links_json() working."""
    with open("src/tests/data/input/truesec.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--json",
            "--json-description",
            "preamble",
            "https://www.truesec.com/hub/blog",
        ]
    )
    links = rss.extract_links_json(soup, arguments)
    with open("src/tests/data/output/truesec", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_json_no_match_description():
    """Test extract_links_json() working."""
    with open("src/tests/data/input/truesec.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--json",
            "--json-description",
            "description",
            "https://www.truesec.com/hub/blog",
        ]
    )
    links = rss.extract_links_json(soup, arguments)
    with open("src/tests/data/output/truesec_no_desc", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_json_no_json(example_html_string):
    """Test extract_links_json() with no json."""
    soup = BeautifulSoup(example_html_string, "html.parser")
    arguments = rss.parse_arguments(["--json", "https://www.truesec.com/hub/blog"])
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.extract_links_json(soup, arguments)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_extract_links_json_no_title():
    """Test extract_links_json() with no title."""
    with open("src/tests/data/input/truesec.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        ["--json", "--json-title", "fail", "https://www.truesec.com/hub/blog"]
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.extract_links_json(soup, arguments)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_create_rss_feed():
    """Test create_rss_feed() in RSS format working."""
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


def test_create_rss_feed_atom():
    """Test create_rss_feed() with Atom output format."""
    with open("src/tests/data/output/apple.xml", "r", encoding="utf-8") as f:
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
        ]
    )
    with open("src/tests/data/output/apple", "rb") as f:
        links = pickle.load(f)
    rss_feed = rss.create_rss_feed(links, arguments)

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
    with open("src/tests/data/output/tripwire.xml", "r", encoding="utf-8") as f:
        correct_rss_feed = f.read()
    arguments = rss.parse_arguments(
        [
            "--title",
            "Tripwire",
            "--html",
            "--base-url",
            "https://www.tripwire.com",
            "http://www.tripwire.com/state-of-security",
        ]
    )
    rss_feed = rss.create_rss_feed(links, arguments)
    rss_feed = re.sub(
        r"<lastBuildDate>.*</lastBuildDate>",
        "<lastBuildDate>Sun, 23 Apr 2023 13:33:02 +0000</lastBuildDate>",
        rss_feed,
    )
    assert rss_feed == correct_rss_feed


def test_save_rss_feed_working(tmpdir):
    """Test save_rss_feed() in RSS format."""
    test_output = tmpdir.mkdir("sub").join("tripwire.xml")
    arguments = rss.parse_arguments(
        [
            "--output",
            str(test_output),
            "--html",
            "--base-url",
            "https://www.tripwire.com",
            "http://www.tripwire.com/state-of-security",
        ]
    )
    with open("src/tests/data/output/tripwire.xml", "r", encoding="utf-8") as f:
        rss_feed = f.read()
    rss.save_rss_feed(rss_feed, arguments)

    assert test_output.read_text(encoding="utf-8") == rss_feed


def test_save_atom_feed_working(tmpdir):
    """Test save_rss_feed() in Atom format."""
    test_output = tmpdir.mkdir("sub").join("apple.xml")
    arguments = rss.parse_arguments(
        [
            "--title",
            "Apple Security",
            "--atom",
            "--output",
            str(test_output),
            "--json",
            "--json-entries",
            "blogs",
            "--json-url",
            "slug",
            "--base-url",
            "https://security.apple.com/blog/",
            "https://security.apple.com/blog",
        ]
    )
    with open("src/tests/data/output/apple.xml", "r", encoding="utf-8") as f:
        rss_feed = f.read()
    rss.save_rss_feed(rss_feed, arguments)

    assert test_output.read_text(encoding="utf-8") == rss_feed


def test_save_rss_feed_not_working():
    """Test save_rss_feed() and check that it fails."""
    test_output = "/root/tripwire.xml"
    arguments = rss.parse_arguments(
        [
            "--output",
            test_output,
            "--html",
            "--base-url",
            "https://www.tripwire.com",
            "http://www.tripwire.com/state-of-security",
        ]
    )
    with open("src/tests/data/output/tripwire.xml", "r", encoding="utf-8") as f:
        rss_feed = f.read()

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.save_rss_feed(rss_feed, arguments)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_init():
    """Test init() function."""
    with patch.object(rss, "main", return_value=42):
        with patch.object(rss, "__name__", "__main__"):
            with patch.object(rss.sys, "exit") as mock_exit:
                rss.init()
                assert mock_exit.call_args[0][0] == 42
