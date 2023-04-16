# rssfixer

A small tool to generate an [RSS][rss] feed from some [Wordpress][wor] blogs that for some reason don't generate their own feeds.

## Installation

```bash
pip install rssfixer
```

## Usage

An example to generate a feed for [nccgroup][ncc]:

```bash
$ ./venv/bin/rssfixer --title nccgroup https://research.nccgroup.com/                                                                                                           ✔ ╱ tmp  ╱ 14:49:39 
RSS feed created: rss_feed.xml
```

You can specify a filename and silence output:

```bash
$ rssfixer --title nccgroup --output nccgroup.xml --quiet https://research.nccgroup.com/
```

The resulting file is available [here][exa] as an example.


  [exa]: https://github.com/reuteras/rssfixer/blob/main/example/nccgroup.xml
  [ncc]: https://research.nccgroup.com/
  [rss]: https://www.rssboard.org/
  [wor]: https://wordpress.org/
