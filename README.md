# rssfixer

A small tool to generate an [RSS][rss] feed from some [Wordpress][wor] blogs that for some reason don't generate their own feeds.

## Installation

```bash
pip install rssfixer
```

## Usage

An example to generate a feed for [nccgroup][ncc]:

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

  [exa]: https://github.com/reuteras/rssfixer/blob/main/example/nccgroup.xml
  [ncc]: https://research.nccgroup.com/
  [rss]: https://www.rssboard.org/
  [wor]: https://wordpress.org/
