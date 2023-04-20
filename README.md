# rssfixer

[![GitHub Super-Linter](https://github.com/reuteras/rssfixer/actions/workflows/linter.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)
![PyPI](https://img.shields.io/pypi/v/rssfixer?color=green)
[![CodeQL](https://github.com/reuteras/rssfixer/workflows/CodeQL/badge.svg)](https://github.com/reuteras/rssfixer/actions?query=workflow%3ACodeQL)

A small tool to generate an [RSS][rss] feed from some [WordPress][wor] blogs that for some reason don't generate their own feeds. This tool uses [BeautifulSoup][bso] to parse the HTML and [feedgen][fge] to generate the feed.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install rssfixer
```

## Example

Format for storing the links varies but I'll try and add more formats as I find them.

### List

An example to generate a feed for [nccgroup][ncc] that have the links in a list:

```bash
$ rssfixer --title nccgroup https://research.nccgroup.com/
RSS feed created: rss_feed.xml
```

You can specify a filename and silence output:

```bash
rssfixer --title nccgroup --output nccgroup.xml --quiet https://research.nccgroup.com/
```

The resulting file is available [here][exa] as an example.

Most times you would run the script from crontab to have an updated feed. Here is an example with a venv in _/home/user/src/rssfixer_.

```bash
32 * * * *      /home/user/src/rssfixer/bin/rssfixer --title nccgroup --output /var/www/html/feeds/nccgroup.xml --quiet https://research.nccgroup.com
```

### JSON

An example for [truesec.com][tru]:

```bash
rssfixer --json --quiet --output truesec.xml https://www.truesec.com/hub/blog
```

### Usage

```Text
usage: rssfixer [-h] [--version] [--atom] [--base-url BASE_URL] [--html] [--html-entries HTML_ENTRIES] [--html-url HTML_URL] [--html-title HTML_TITLE]
                [--html-title-class HTML_TITLE_CLASS] [--html-description HTML_DESCRIPTION] [--html-description-class HTML_DESCRIPTION_CLASS] [--json] [--json-entries JSON_ENTRIES]
                [--json-url JSON_URL] [--json-title JSON_TITLE] [--json-description JSON_DESCRIPTION] [--output OUTPUT] [--title TITLE] [-q] [--list]
                url

Generate RSS feed for blog that don't publish a feed. Default is to find links in a simple <ul>-list. Options are available to find links in other HTML elements or JSON strings.

positional arguments:
  url                   URL for the blog

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --atom                Generate Atom feed
  --base-url BASE_URL   Base URL for the blog
  --html                Find entries in HTML
  --html-entries HTML_ENTRIES
                        HTML selector for entries
  --html-url HTML_URL   HTML selector for URL
  --html-title HTML_TITLE
                        HTML selector for title
  --html-title-class HTML_TITLE_CLASS
                        Flag to specify title class (regex)
  --html-description HTML_DESCRIPTION
                        HTML selector for description
  --html-description-class HTML_DESCRIPTION_CLASS
                        Flag to specify description class (regex)
  --json                Find entries in JSON
  --json-entries JSON_ENTRIES
                        JSON key for entries (default: 'entries')
  --json-url JSON_URL   JSON key for URL (default: 'url')
  --json-title JSON_TITLE
                        JSON key for title
  --json-description JSON_DESCRIPTION
                        JSON key for description
  --output OUTPUT       Name of the output file
  --title TITLE         Title of the RSS feed (default: "My RSS Feed")
  -q, --quiet           Suppress output
  --list                Find entries in HTML <ul>-list (default)
```


  [bso]: https://www.crummy.com/software/BeautifulSoup/
  [exa]: https://github.com/reuteras/rssfixer/blob/main/example/nccgroup.xml
  [fge]: https://feedgen.kiesow.be/ 
  [ncc]: https://research.nccgroup.com/
  [rss]: https://www.rssboard.org/
  [tru]: https://www.truesec.com/hub/blog
  [wor]: https://wordpress.org/
