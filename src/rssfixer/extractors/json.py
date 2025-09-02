"""JSON extractor for links in JSON data embedded in HTML."""

import json
from typing import Any

from bs4 import BeautifulSoup

from ..exceptions import JSONParsingError
from ..models import LinkEntry
from .base import LinkExtractor


class JsonExtractor(LinkExtractor):
    """Extractor for links in JSON data embedded in HTML pages."""

    def extract_links(self, soup: BeautifulSoup) -> list[LinkEntry]:
        """Extract links from JSON data in HTML.

        Args:
            soup: Parsed HTML content

        Returns:
            List of LinkEntry objects from JSON data

        Raises:
            JSONParsingError: If JSON parsing fails or required keys missing
            NoLinksFoundError: If no links are found

        """
        entries = self._find_json_entries(soup)
        if entries is None:
            raise JSONParsingError("Unable to find JSON object with entries")

        links = []

        # Extract links from JSON entries
        for entry in entries:
            if not isinstance(entry, dict):
                continue

            try:
                url = entry[self.arguments.json_url]
                title = entry[self.arguments.json_title]

                if not url or not title:
                    continue

            except KeyError as e:
                raise JSONParsingError(f"Required JSON key missing: {e}") from e

            # Extract description if available
            description = entry.get(self.arguments.json_description, "")

            entry_obj = self._add_unique_link(url, title, description)
            if entry_obj:
                links.append(entry_obj)

        return self._validate_links(links)

    def _find_json_entries(self, soup: BeautifulSoup) -> list[dict[str, Any]] | None:
        """Find JSON entries in script tags.

        Args:
            soup: Parsed HTML content

        Returns:
            List of entries from JSON data, or None if not found

        """
        # Find JSON string in the page
        for json_script in soup.find_all("script", type="application/json"):
            try:
                if not json_script.text.strip():
                    continue

                json_object = json.loads(json_script.text)
                entries = self._find_entries_recursive(json_object, self.arguments.json_entries)
                if entries is not None and isinstance(entries, list):
                    return entries
            except (json.JSONDecodeError, AttributeError):
                continue

        return None

    def _find_entries_recursive(self, json_object: Any, entries_key: str) -> list[dict[str, Any]] | None:
        """Recursively find entries in JSON object.

        Args:
            json_object: JSON data structure to search
            entries_key: Key to search for

        Returns:
            List of entries if found, None otherwise

        """
        if isinstance(json_object, dict):
            for key, value in json_object.items():
                if key == entries_key and isinstance(value, list):
                    return value
                result = self._find_entries_recursive(value, entries_key)
                if result is not None:
                    return result
        elif isinstance(json_object, list):
            for item in json_object:
                result = self._find_entries_recursive(item, entries_key)
                if result is not None:
                    return result

        return None
