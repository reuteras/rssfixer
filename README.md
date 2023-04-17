# rssfixer

A small tool to generate an [RSS][rss] feed from some [Wordpress][wor] blogs that for some reason don't generate their own feeds.

## Installation

```bash
pip install rssfixer
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
$ rssfixer --title nccgroup --output nccgroup.xml --quiet https://research.nccgroup.com/
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

```bash
usage: rssfixer [-h] [--json] [--json-entries JSON_ENTRIES] [--json-url JSON_URL] [--json-title JSON_TITLE] [--json-description JSON_DESCRIPTION] [--output OUTPUT]
                [--title TITLE] [-q]
                url

Generate RSS feed for blog that don't publish a feed

positional arguments:
  url                   URL for the blog

options:
  -h, --help            show this help message and exit
  --json                Find entries in JSON
  --json-entries JSON_ENTRIES
                        JSON key for entries (default: 'entries')
  --json-url JSON_URL   JSON key for URL (default: 'url')
  --json-title JSON_TITLE
                        JSON key for title (default: 'title')
  --json-description JSON_DESCRIPTION
                        JSON key for description (default: 'preamble')
  --output OUTPUT       Name of the output file (default: "rss_feed.xml")
  --title TITLE         Title of the RSS feed (default: "My RSS Feed")
  -q, --quiet           Suppress output
```


  [exa]: https://github.com/reuteras/rssfixer/blob/main/example/nccgroup.xml
  [ncc]: https://research.nccgroup.com/
  [rss]: https://www.rssboard.org/
  [tru]: https://www.truesec.com/hub/blog
  [wor]: https://wordpress.org/
