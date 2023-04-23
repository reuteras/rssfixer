# rssfixer

[![GitHub Super-Linter](https://github.com/reuteras/rssfixer/actions/workflows/linter.yml/badge.svg)](https://github.com/marketplace/actions/super-linter)
![PyPI](https://img.shields.io/pypi/v/rssfixer?color=green)
[![CodeQL](https://github.com/reuteras/rssfixer/workflows/CodeQL/badge.svg)](https://github.com/reuteras/rssfixer/actions?query=workflow%3ACodeQL)
[![Coverage](https://raw.githubusercontent.com/reuteras/rssfixer/main/resources/coverage.svg)](https://github.com/reuteras/rssfixer/)

A small tool to generate an [RSS][rss] feed from some [WordPress][wor] blogs that for some reason don't generate their own feeds. This tool uses [BeautifulSoup][bso] to parse the HTML and [feedgen][fge] to generate the feed.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install rssfixer
```

## Example

Format for storing the links varies but I'll try and add more formats as I find them.

### Simple list

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

### General HTML

An example for [tripwire.com][tri]:

```bash
rssfixer --title Tripwire --output tripwire.xml --quiet --html --base-url https://www.tripwire.com http://www.tripwire.com/state-of-security

```


### Usage

Command line options:

<!-- CODE:START -->
echo '```Text'
rssfixer --help
echo '```'
<!-- CODE:END -->

<!-- OUTPUT:START -->
This content will be replaced by the output of the code block above.
<!-- OUTPUT:END -->

## Command line examples for some blogs

### Apple Security Blog

Url: [https://security.apple.com/blog/][app]

```bash
rssfixer --title "Apple Security" --output apple.xml --quiet --json --json-entries blogs --json-url slug --base-url https://security.apple.com/blog/ https://security.apple.com/blog
```

### nccgroup

Url: [https://research.nccgroup.com/][ncc]

```bash
rssfixer --title nccgroup --output nccgroup.xml --quiet https://research.nccgroup.com
```

or you can specify _--list__ to find the links in a list which is the default:

```bash
rssfixer --title nccgroup --output nccgroup.xml --quiet --list https://research.nccgroup.com
```

### Tripwire

Url: [https://www.tripwire.com/state-of-security][tri]

```bash
rssfixer --title Tripwire --output tripwire.xml --quiet --html --base-url https://www.tripwire.com http://www.tripwire.com/state-of-security
```

### TrueSec

Url: [https://www.truesec.com/hub/blog][tru]

```bash
rssfixer --title Truesec --output truesec.xml --quiet --json --json-description preamble https://www.truesec.com/hub/blog
```

## Setup blogs

During testing it is useful to use --stdout to see the generated feed. 


  [app]: https://security.apple.com/blog/
  [bso]: https://www.crummy.com/software/BeautifulSoup/
  [exa]: https://github.com/reuteras/rssfixer/blob/main/src/tests/data/output/nccgroup.xml
  [fge]: https://feedgen.kiesow.be/
  [ncc]: https://research.nccgroup.com/
  [rss]: https://www.rssboard.org/
  [tri]: https://www.tripwire.com/state-of-security
  [tru]: https://www.truesec.com/hub/blog
  [wor]: https://wordpress.org/
