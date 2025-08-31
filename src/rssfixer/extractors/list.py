"""List extractor for links in HTML <ul> elements."""


from bs4 import BeautifulSoup

from ..models import LinkEntry
from .base import LinkExtractor


class ListExtractor(LinkExtractor):
    """Extractor for links in HTML <ul>-lists."""

    EXCLUDED_URL_PATTERNS = ["/category/", "/author/"]

    def extract_links(self, soup: BeautifulSoup) -> list[LinkEntry]:
        """Extract links from <ul> lists in HTML.
        
        Args:
            soup: Parsed HTML content
            
        Returns:
            List of LinkEntry objects from <ul> elements
            
        Raises:
            NoLinksFoundError: If no links are found

        """
        links = []

        # Iterate through all the <ul> elements in the page
        for links_list in soup.find_all("ul", class_=None):
            for li in links_list.find_all("li"):
                link = li.find("a")
                if not link or "href" not in link.attrs:
                    continue

                url = link["href"]
                title = link.text.strip()

                if not url or not title:
                    continue

                # Exclude URLs containing specified patterns
                if any(pattern in url for pattern in self.EXCLUDED_URL_PATTERNS):
                    continue

                # Use title as description for list items
                description = title

                entry = self._add_unique_link(url, title, description)
                if entry:
                    links.append(entry)

        return self._validate_links(links)
