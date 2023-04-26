import pytest
from rssfixer import rss


def test_rss_args_html_json_entries():
    """Test rss_args function"""
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
    """Test rss_args function"""
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
