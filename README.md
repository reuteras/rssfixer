# rssfixer

<!-- CODE:BASH:START -->
<!-- echo '[![GitHub Super-Linter](https://github.com/reuteras/rssfixer/actions/workflows/linter.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)' -->
<!-- echo '![PyPI](https://img.shields.io/pypi/v/rssfixer?color=green)' -->
<!-- echo '[![CodeQL](https://github.com/reuteras/rssfixer/workflows/CodeQL/badge.svg)](https://github.com/reuteras/rssfixer/actions?query=workflow%3ACodeQL)' -->
<!-- echo '[![Coverage](https://raw.githubusercontent.com/reuteras/rssfixer/main/resources/coverage.svg)](https://github.com/reuteras/rssfixer/)' -->
<!-- echo '[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/reuteras/rssfixer/main.svg)](https://results.pre-commit.ci/latest/github/reuteras/rssfixer/main)' -->
<!-- if jq '.metrics._totals | ."SEVERITY.HI"' resources/bandit.json|grep -vE '^0' > /dev/null;then cl='red';elif jq '.metrics._totals' resources/bandit.json|grep "SEVERITY"|grep -E ' 0,'|wc -l|grep -vE '4$' > /dev/null;then cl='yellow';else cl='green';fi echo -n '[![security: bandit](https://img.shields.io/badge/security-bandit-' + $cl + '.svg)](https://github.com/PyCQA/bandit)' -->
<!-- CODE:END -->
<!-- OUTPUT:START -->
<!-- ⚠️ This content is auto-generated by `markdown-code-runner`. -->
[![GitHub Super-Linter](https://github.com/reuteras/rssfixer/actions/workflows/linter.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)
![PyPI](https://img.shields.io/pypi/v/rssfixer?color=green)
[![CodeQL](https://github.com/reuteras/rssfixer/workflows/CodeQL/badge.svg)](https://github.com/reuteras/rssfixer/actions?query=workflow%3ACodeQL)
[![Coverage](https://raw.githubusercontent.com/reuteras/rssfixer/main/resources/coverage.svg)](https://github.com/reuteras/rssfixer/)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/reuteras/rssfixer/main.svg)](https://results.pre-commit.ci/latest/github/reuteras/rssfixer/main)

<!-- OUTPUT:END -->

A tool to generate an [RSS][rss] feed from some [WordPress][wor] blogs and other sources that for some reason don't generate their own feeds. This tool uses [BeautifulSoup][bso] to parse the HTML and [feedgen][fge] to generate the feed. I created this tool to be to follow news from companies that have forgotten the usefulness of RSS.

## Installation

Create a virtual environment and simply run `python3 -m pip install rssfixer`, full example below.

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install rssfixer
```

## Supported page types

I've expanded the tools to blogs that I like to follow. If you have suggestions to add/change functionality please open an [issue][iss] or start a new [discussion][dis].

The basic formats of supported web pages are:

- `--list` - links are in simple ul-list
- `--json` - links, titles and sometimes description is accessible in a JSON structure
- `--html` - links and titles can be found by some unique HTML element
- `--release` - similar to `--html` except there are no links and you have to specify a target URL

During testing it is useful to use `--stdout`option to see the generated feed. When I have time (and enough motivation) I might write a tool to try and find the right combination of options for a specified URL.

### Simple list

An example to generate a feed for [nccgroup][ncc] that have the links in a simple ul-list by using the `--list` option:

```bash
$ rssfixer --title nccgroup --list https://research.nccgroup.com/
RSS feed created: rss_feed.xml
```

You can specify a filename and silence output:

```bash
rssfixer --title nccgroup --output nccgroup.xml --quiet https://research.nccgroup.com/
```

The resulting file is available [here][exa] as an example.

Most times you would run the script from crontab to have an updated feed. Here is an example with a venv in _/home/user/src/rssfixer_.

```bash
32 * * * *      /home/user/src/rssfixer/bin/rssfixer --title nccgroup --output /var/www/html/feeds/nccgroup.xml --quiet --list https://research.nccgroup.com
```

### JSON

Some blogs like [truesec.com][tru] have all blog links in a JSON object. You can use the `--json` option to parse the JSON object and generate a feed. The same is true for Apple's [security blog][app] page.

An example for [Apple][app]:

```bash
rssfixer --title "Apple Security" --output apple.xml --quiet --json --json-entries blogs --json-url slug --base-url https://security.apple.com/blog/ https://security.apple.com/blog
```

In this example `--json-entries blogs`specifies that blog entries are located in a key called __blogs__ and that URLs are available in a key called __slug__. Since the URL only includes the key (or slug) we specify the full URL to the blog with `--base-url https://security.apple.com/blog/`.

An example for [truesec.com][tru]:

```bash
rssfixer --title Truesec --json --json-description preamble --quiet --output truesec.xml https://www.truesec.com/hub/blog
```

Here we must specify `--json-description preamble` to find the description or summary of the blog post.

### General HTML

Pages with a more general HTML structure can be parsed with the `--html` option. You can specify the HTML tag for the entries, the URL and title of the blog entry.

An example for [tripwire.com][tri]:

```bash
rssfixer --title Tripwire --output tripwire.xml --quiet --html --base-url https://www.tripwire.com http://www.tripwire.com/state-of-security
```

### Release

Check for one entity on release pages like [SQLite][sql] (h3) and generate RSS feed with links to the download page (required argument `--release-url`). Easy way to get notified when a new version is released.

```bash
rssfixer --release --output sqlite.xml --release-entries h3 --release-url https://sqlite.org/download.html https://sqlite.org/changes.html
```

### Usage

Command-line options (updated on commit by [markdown-code-runner][mcr]):

<!-- CODE:BASH:START -->
<!-- echo '```Text' -->
<!-- poetry run rssfixer --help -->
<!-- echo '```' -->
<!-- CODE:END -->

<!-- OUTPUT:START -->
<!-- ⚠️ This content is auto-generated by `markdown-code-runner`. -->
```Text
usage: rssfixer [-h] (--html | --json | --list | --release) [--version]
                [--atom] [--base-url BASE_URL] [--release-url RELEASE_URL]
                [--release-entries RELEASE_ENTRIES]
                [--html-entries HTML_ENTRIES]
                [--html-entries-class HTML_ENTRIES_CLASS]
                [--html-url HTML_URL] [--html-title HTML_TITLE]
                [--html-title-class HTML_TITLE_CLASS]
                [--title-filter TITLE_FILTER]
                [--html-description HTML_DESCRIPTION]
                [--html-description-class HTML_DESCRIPTION_CLASS]
                [--json-entries JSON_ENTRIES] [--json-url JSON_URL]
                [--json-title JSON_TITLE]
                [--json-description JSON_DESCRIPTION] [--output OUTPUT]
                [--title TITLE] [--user-agent USER_AGENT]
                [--filter-type FILTER_TYPE] [--filter-name FILTER_NAME] [-q]
                [-d] [--stdout]
                url

Generate RSS feed for blog that don't publish a feed. Default is to find links
in a simple <ul>-list. Options are available to find links in other HTML
elements or JSON strings.

positional arguments:
  url                   URL for the blog

options:
  -h, --help            show this help message and exit
  --html                Find entries in HTML
  --json                Find entries in JSON
  --list                Find entries in HTML <ul>-list (default)
  --release             Find releases in HTML
  --version             show program's version number and exit
  --atom                Generate Atom feed
  --base-url BASE_URL   Base URL for the blog
  --release-url RELEASE_URL
                        Release URL for downloads
  --release-entries RELEASE_ENTRIES
                        Release selector for entries
  --html-entries HTML_ENTRIES
                        HTML selector for entries
  --html-entries-class HTML_ENTRIES_CLASS
                        Class name for entries
  --html-url HTML_URL   HTML selector for URL
  --html-title HTML_TITLE
                        HTML selector for title
  --html-title-class HTML_TITLE_CLASS
                        Flag to specify title class (regex)
  --title-filter TITLE_FILTER
                        Filter for title, ignore entries that don't match
  --html-description HTML_DESCRIPTION
                        HTML selector for description
  --html-description-class HTML_DESCRIPTION_CLASS
                        Flag to specify description class (regex)
  --json-entries JSON_ENTRIES
                        JSON key for entries (default: 'entries')
  --json-url JSON_URL   JSON key for URL (default: 'url')
  --json-title JSON_TITLE
                        JSON key for title
  --json-description JSON_DESCRIPTION
                        JSON key for description
  --output OUTPUT       Name of the output file
  --title TITLE         Title of the RSS feed (default: "My RSS Feed")
  --user-agent USER_AGENT
                        User agent to use for HTTP requests
  --filter-type FILTER_TYPE
                        Filter web page
  --filter-name FILTER_NAME
                        Filter web page
  -q, --quiet           Suppress output
  -d, --debug           Debug selection
  --stdout              Print to stdout
```

<!-- OUTPUT:END -->

## Command-line examples for blogs

```bash
# Apple Security Blog
# Url: https://security.apple.com/blog/
rssfixer --title "Apple Security" --output apple.xml --quiet --json --json-entries blogs --json-url slug --base-url https://security.apple.com/blog/ https://security.apple.com/blog

# nccgroup
# Url: https://research.nccgroup.com/
rssfixer --title nccgroup --output nccgroup.xml --quiet --list https://research.nccgroup.com

# Tripwire
# Url: https://www.tripwire.com/state-of-security
rssfixer --title Tripwire --output tripwire.xml --quiet --html --base-url https://www.tripwire.com http://www.tripwire.com/state-of-security

# TrueSec
# Url: https://www.truesec.com/hub/blog
rssfixer --title Truesec --output truesec.xml --quiet --json --json-description preamble https://www.truesec.com/hub/blog

# SQLite
# Url: https://sqlite.org/changes.html
rssfixer --title SQLite --release --release-entries h3 --release-url https://sqlite.org/download.html https://sqlite.org/changes.html

# Nucleus
# https://nucleussec.com/category/cisa-kev
rssfixer --title "Nucleus CISA KEV" --output nucleus.xml  --html --filter-type div --filter-name recent-post-widget --html-entries div --html-title div --html-title-class "post-desc" --title-filter KEV https://nucleussec.com/category/cisa-kev

# NCSC-SE
# https://www.ncsc.se/publikationer/
rssfixer --html --filter-type div --filter-name 'page-container' --html-entries div --html-entries-class "news-text" --html-title h2 --html-title-class "" --html-description p --html-description-class "" --html-url a --base-url https://www.ncsc.se --stdout  --atom --title "Feed for NCSC-SE" https://www.ncsc.se/publikationer/
```

If you have other example use case please add them in [show usage examples][sue] in discussions.


  [app]: https://security.apple.com/blog/
  [bso]: https://www.crummy.com/software/BeautifulSoup/
  [dis]: https://github.com/reuteras/rssfixer/discussions
  [exa]: https://github.com/reuteras/rssfixer/blob/main/src/tests/data/output/nccgroup.xml
  [fge]: https://feedgen.kiesow.be/
  [iss]: https://github.com/reuteras/rssfixer/issues
  [mcr]: https://github.com/basnijholt/markdown-code-runner
  [ncc]: https://research.nccgroup.com/
  [rss]: https://www.rssboard.org/
  [sql]: https://sqlite.org/changes.html
  [sue]: https://github.com/reuteras/rssfixer/discussions/categories/show-usage-examples
  [tri]: https://www.tripwire.com/state-of-security
  [tru]: https://www.truesec.com/hub/blog
  [wor]: https://wordpress.org/
