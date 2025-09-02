"""Release extractor for release pages with version information."""

import hashlib

from bs4 import BeautifulSoup

from ..models import LinkEntry
from .base import LinkExtractor


class ReleaseExtractor(LinkExtractor):
    """Extractor for release pages with version titles."""

    def __init__(self, arguments):
        """Initialize extractor with arguments.

        Args:
            arguments: Parsed command line arguments

        """
        super().__init__(arguments)
        self._unique_titles: set[str] = set()

    def extract_links(self, soup: BeautifulSoup) -> list[LinkEntry]:
        """Extract links from release page elements.

        Args:
            soup: Parsed HTML content

        Returns:
            List of LinkEntry objects for releases

        Raises:
            NoLinksFoundError: If no links are found

        """
        links = []

        # Iterate through all elements of the specified type
        for entry in soup.find_all(self.arguments.release_entries):
            title = entry.text.strip()
            if not title:
                continue

            # Check for unique titles (not URLs like other extractors)
            if title in self._unique_titles:
                continue

            self._unique_titles.add(title)

            try:
                # Generate unique URL using title hash
                url = self._generate_release_url(title)
                entry_obj = LinkEntry(url=url, title=title, description="")
                links.append(entry_obj)
            except (ValueError, UnicodeEncodeError):
                # Skip entries with invalid characters
                continue

        return self._validate_links(links)

    def _generate_release_url(self, title: str) -> str:
        """Generate a unique URL for a release title.

        Args:
            title: Release title

        Returns:
            URL with hash parameter for uniqueness

        Raises:
            ValueError: If title cannot be encoded

        """
        try:
            title_bytes = title.encode("utf-8")
            title_hash = hashlib.sha256(title_bytes)
            title_sha256 = title_hash.hexdigest()
            return f"{self.arguments.release_url}?{title_sha256}"
        except UnicodeEncodeError as e:
            raise ValueError(f"Cannot encode title: {title}") from e
