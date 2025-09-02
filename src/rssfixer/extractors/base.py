"""Abstract base class for link extractors."""

from abc import ABC, abstractmethod

from bs4 import BeautifulSoup

from ..exceptions import NoLinksFoundError
from ..models import LinkEntry


class LinkExtractor(ABC):
    """Abstract base class for extracting links from web pages."""

    def __init__(self, arguments):
        """Initialize extractor with parsed command line arguments.

        Args:
            arguments: Parsed command line arguments

        """
        self.arguments = arguments
        self._unique_links: set[str] = set()

    @abstractmethod
    def extract_links(self, soup: BeautifulSoup) -> list[LinkEntry]:
        """Extract links from parsed HTML.

        Args:
            soup: Parsed HTML content using BeautifulSoup

        Returns:
            List of LinkEntry objects

        Raises:
            NoLinksFoundError: If no links are found or extraction fails

        """
        pass

    def _add_unique_link(self, url: str, title: str, description: str = "") -> LinkEntry | None:
        """Add a link if it's unique.

        Args:
            url: The link URL
            title: The link title
            description: Optional description

        Returns:
            LinkEntry if added, None if duplicate

        Raises:
            ValueError: If URL or title is invalid

        """
        if url in self._unique_links:
            return None

        self._unique_links.add(url)
        return LinkEntry(url=url, title=title, description=description)

    def _validate_links(self, links: list[LinkEntry]) -> list[LinkEntry]:
        """Validate that links were found.

        Args:
            links: List of extracted links

        Returns:
            The same list if valid

        Raises:
            NoLinksFoundError: If no links found

        """
        if not links:
            raise NoLinksFoundError("No links found during extraction")
        return links
