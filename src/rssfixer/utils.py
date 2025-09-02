"""Utility functions for RSS fixer."""

import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .exceptions import FileWriteError, HTMLParsingError, NetworkError


def fetch_html(url: str, headers: dict[str, str], timeout: int = 10) -> str:
    """Fetch HTML content from a URL.

    Args:
        url: URL to fetch
        headers: HTTP headers to send
        timeout: Request timeout in seconds

    Returns:
        HTML content as string

    Raises:
        NetworkError: If request fails

    """
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout as e:
        raise NetworkError(f"Request timed out for {url}") from e
    except requests.exceptions.ConnectionError as e:
        raise NetworkError(f"Unable to connect to {url}") from e
    except requests.exceptions.RequestException as e:
        raise NetworkError(f"Request failed for {url}: {e}") from e


def filter_html(soup: BeautifulSoup, filter_type: str, filter_name: str | None) -> BeautifulSoup:
    """Filter web page content by HTML element type and name.

    Args:
        soup: Parsed HTML content
        filter_type: HTML element type to filter by
        filter_name: Element name/class to filter by (optional)

    Returns:
        Filtered BeautifulSoup object

    Raises:
        HTMLParsingError: If no entries found

    """
    if filter_name is None:
        filtered_elements = soup.find_all(filter_type)
    else:
        filtered_elements = soup.find_all(filter_type, filter_name)

    if not filtered_elements:
        raise HTMLParsingError(f"No entries found for filter {filter_type}:{filter_name}")

    return BeautifulSoup(str(filtered_elements), "html.parser")


def safe_find_text(element, selector: str, class_name: str | None = None, default: str = "") -> str:
    """Safely extract text from HTML element.

    Args:
        element: BeautifulSoup element to search within
        selector: HTML selector to find
        class_name: Optional class name to match
        default: Default value if element not found

    Returns:
        Extracted text or default value

    """
    try:
        if class_name:
            found = element.find(selector, re.compile(class_name))
        else:
            found = element.find(selector)
        return found.text.strip() if found else default
    except (AttributeError, TypeError):
        return default


def save_rss_feed(rss_feed: str, output_path: str, is_atom: bool = False, quiet: bool = False) -> None:
    """Save the RSS feed to a file.

    Args:
        rss_feed: RSS feed content as string
        output_path: Path to save the file
        is_atom: Whether this is an Atom feed (for messaging)
        quiet: Whether to suppress output messages

    Raises:
        FileWriteError: If file writing fails

    """
    try:
        with Path(output_path).open("w", encoding="utf-8") as f:
            f.write(rss_feed)
    except OSError as e:
        raise FileWriteError(f"Unable to write to file {output_path}") from e

    if not quiet:
        feed_type = "Atom" if is_atom else "RSS"
        print(f"{feed_type} feed created: {output_path}")
