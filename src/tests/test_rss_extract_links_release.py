import pickle

import pytest
from bs4 import BeautifulSoup
from rssfixer import rss


def test_extract_links_release():
    """Test extract_links_release - should return correct links"""
    with open("src/tests/data/input/sqlite.html", "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--release",
            "--release-entries",
            "h3",
            "--release-url",
            "https://sqlite.org/download.html",
            "https://sqlite.org/changes.html",
        ]
    )
    links = rss.extract_links_release(soup, arguments)
    with open("src/tests/data/output/sqlite", "rb") as f:
        correct_links = pickle.load(f)
    assert links == correct_links


def test_extract_links_release_no_title_text():
    """Test extract_links_html where there are no title texts - should fail"""
    content = """<html>
    <body>
        <h3></h3>
    </body>
    </html>"""
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--release",
            "--release-entries",
            "h3",
            "--release-url",
            "https://sqlite.org/download.html",
            "https://sqlite.org/changes.html",
        ]
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.extract_links_release(soup, arguments)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_extract_links_release_no_match():
    """Test extract_links_html where there are no matching release-entries - should fail"""
    content = """<html>
    <body>
        <p></p>
    </body>
    </html>"""
    soup = BeautifulSoup(content, "html.parser")
    arguments = rss.parse_arguments(
        [
            "--release",
            "--release-entries",
            "div",
            "--release-url",
            "https://sqlite.org/download.html",
            "https://sqlite.org/changes.html",
        ]
    )
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.extract_links_release(soup, arguments)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
