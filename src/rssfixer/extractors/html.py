"""HTML extractor for links in specific HTML elements."""

import re

from bs4 import BeautifulSoup

from ..models import LinkEntry
from ..utils import safe_find_text
from .base import LinkExtractor


class HtmlExtractor(LinkExtractor):
    """Extractor for links in specific HTML elements."""

    def extract_links(self, soup: BeautifulSoup) -> list[LinkEntry]:
        """Extract links from specific HTML elements.

        Args:
            soup: Parsed HTML content

        Returns:
            List of LinkEntry objects from HTML elements

        Raises:
            NoLinksFoundError: If no links are found

        """
        links = []

        # Iterate through all elements of the specified type
        for entry in soup.find_all(self.arguments.html_entries, self.arguments.html_entries_class):
            # Extract URL safely
            url = self._get_html_url(entry)
            if not url:
                continue

            # Extract title safely
            title = self._get_html_title(entry)
            if not title:
                continue

            # Apply title filter if specified
            if self.arguments.title_filter:
                if not re.search(self.arguments.title_filter, title):
                    continue

            # Extract description safely
            description = self._get_html_description(entry)

            entry_obj = self._add_unique_link(url, title, description)
            if entry_obj:
                links.append(entry_obj)

        return self._validate_links(links)

    def _get_html_url(self, entry) -> str:
        """Extract URL from HTML entry.

        Args:
            entry: BeautifulSoup element

        Returns:
            URL string or empty string if not found

        """
        try:
            url_elements = entry.find_all(self.arguments.html_url)
            if url_elements and "href" in url_elements[0].attrs:
                return url_elements[0]["href"]
        except (AttributeError, KeyError, IndexError):
            pass
        return ""

    def _get_html_title(self, entry) -> str:
        """Extract title from HTML entry.

        Args:
            entry: BeautifulSoup element

        Returns:
            Title text or empty string if not found

        """
        return safe_find_text(
            entry,
            self.arguments.html_title,
            self.arguments.html_title_class if hasattr(self.arguments, "html_title_class") else None,
        )

    def _get_html_description(self, entry) -> str:
        """Extract description from HTML entry.

        Args:
            entry: BeautifulSoup element

        Returns:
            Description text or empty string if not found

        """
        if not hasattr(self.arguments, "html_description") or not self.arguments.html_description:
            return ""

        return safe_find_text(
            entry,
            self.arguments.html_description,
            self.arguments.html_description_class if hasattr(self.arguments, "html_description_class") else None,
        )
