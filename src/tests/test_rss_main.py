import re

from rssfixer import rss


def test_main_link(capsys, requests_mock):
    """Test the main function."""
    url = "https://research.nccgroup.com/"
    with open("src/tests/data/input/nccgroup.html", "r", encoding="utf-8") as f:
        source = f.read()
    with open("src/tests/data/output/nccgroup.xml", "r", encoding="utf-8") as f:
        result = f.read()
    requests_mock.get(url, text=source)
    args = [
        "--title",
        "nccgroup",
        "--stdout",
        "--list",
        "https://research.nccgroup.com/",
    ]

    rss.main(args)
    captured = re.sub(
        r"<lastBuildDate>.*</lastBuildDate>",
        "<lastBuildDate>Fri, 21 Apr 2023 12:15:48 +0000</lastBuildDate>",
        capsys.readouterr().out,
    )[:-1]
    assert captured == result


def test_main_json(capsys, requests_mock):
    """Test the main function with json arguments."""
    url = "https://security.apple.com/blog"
    with open("src/tests/data/input/apple.html", "r", encoding="utf-8") as f:
        source = f.read()
    with open("src/tests/data/output/apple.xml", "r", encoding="utf-8") as f:
        result = f.read()
    requests_mock.get(url, text=source)
    arguments = [
        "--title",
        "Apple Security",
        "--atom",
        "--json",
        "--json-entries",
        "blogs",
        "--json-url",
        "slug",
        "--stdout",
        "--quiet",
        "--base-url",
        "https://security.apple.com/blog/",
        "https://security.apple.com/blog",
    ]
    rss.main(arguments)
    captured = re.sub(
        r"<updated>.*</updated>",
        "<updated>TIME</updated>",
        capsys.readouterr().out,
    )[:-1]
    result = re.sub(
        r"<updated>.*</updated>",
        "<updated>TIME</updated>",
        result,
    )
    args = rss.parse_arguments(arguments)

    assert captured == result
    assert args.json
    assert args.json_entries == "blogs"
    assert args.json_url == "slug"
    assert args.json_title == "title"
    assert args.json_description == "description"
    assert args.url == "https://security.apple.com/blog"
