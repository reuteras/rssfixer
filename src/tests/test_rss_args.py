import pytest
from rssfixer import rss


def test_rss_args_html_json_entries():
    """Test combination of --html and --json-entries - should fail"""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.parse_arguments(
            [
                "--html",
                "--json-entries",
                "fail",
                "http://www.tripwire.com/state-of-security",
            ]
        )
    assert pytest_wrapped_e.value.code == 2


def test_rss_args_json_html_entries():
    """Test combination of --json and --html-entries - should fail"""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.parse_arguments(
            [
                "--json",
                "--html-entries",
                "fail",
                "http://www.tripwire.com/state-of-security",
            ]
        )
    assert pytest_wrapped_e.value.code == 2


def test_rss_args_list_json_entries():
    """Test combination of --list and --json-entries - should fail"""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.parse_arguments(
            [
                "--list",
                "--json-entries",
                "fail",
                "http://www.tripwire.com/state-of-security",
            ]
        )
    assert pytest_wrapped_e.value.code == 2


def test_rss_args_json_release_entries():
    """Test combination of --json and --release-entries - should fail"""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.parse_arguments(
            [
                "--json",
                "--release-entries",
                "fail",
                "http://www.tripwire.com/state-of-security",
            ]
        )
    assert pytest_wrapped_e.value.code == 2


def test_rss_args_release_html_entries():
    """Test combination of --release and --html-entries - should fail"""
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        rss.parse_arguments(
            [
                "--release",
                "--html-entries",
                "fail",
                "https://sqlite.org/changes.html",
            ]
        )
    assert pytest_wrapped_e.value.code == 2


def test_parse_arguments_required_args():
    """Test argument parsing with --list and url - should succeed"""
    arguments = ["--list", "https://example.com"]
    args = rss.parse_arguments(arguments)
    assert args.list
    assert args.url == "https://example.com"


def test_parse_arguments_optional_args():
    """Test argument parsing with --html and related args - should succeed"""
    arguments = [
        "--html",
        "--html-entries",
        "div.entry",
        "--html-url",
        "a.url",
        "--html-title",
        "h2.title",
        "--html-title-class",
        "custom-title",
        "--html-description",
        "div.description",
        "--html-description-class",
        "custom-description",
        "https://example.com",
    ]
    args = rss.parse_arguments(arguments)
    assert args.html
    assert args.html_entries == "div.entry"
    assert args.html_url == "a.url"
    assert args.html_title == "h2.title"
    assert args.html_title_class == "custom-title"
    assert args.html_description == "div.description"
    assert args.html_description_class == "custom-description"
    assert args.url == "https://example.com"


def test_parse_arguments_json_args():
    """Test argument parsing with --json and related args - should succeed"""
    arguments = [
        "--json",
        "--json-entries",
        "items",
        "--json-url",
        "link",
        "--json-title",
        "name",
        "--json-description",
        "summary",
        "https://example.com",
    ]
    args = rss.parse_arguments(arguments)
    assert args.json
    assert args.json_entries == "items"
    assert args.json_url == "link"
    assert args.json_title == "name"
    assert args.json_description == "summary"
    assert args.url == "https://example.com"


def test_parse_arguments_release_args():
    """Test argument parsing with --release and related args - should succeed"""
    arguments = [
        "--release",
        "--release-entries",
        "items",
        "--release-url",
        "https://example.com/download",
        "https://example.com",
    ]
    args = rss.parse_arguments(arguments)
    assert args.release
    assert args.release_entries == "items"
    assert args.release_url == "https://example.com/download"
    assert args.url == "https://example.com"


def test_parse_arguments_invalid_args_html_json():
    """Test argument parsing with invalid args --html and --json - should fail"""
    with pytest.raises(SystemExit):
        rss.parse_arguments(["--html", "--json", "https://example.com"])


def test_parse_arguments_invalid_args_list_release():
    """Test argument parsing with invalid args --list and --release - should fail"""
    with pytest.raises(SystemExit):
        rss.parse_arguments(["--list", "--release", "https://example.com"])
