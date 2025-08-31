"""Data models for RSS fixer."""

from dataclasses import dataclass


@dataclass
class LinkEntry:
    """Represents a single feed entry with URL, title, and optional description."""

    url: str
    title: str
    description: str | None = ""

    def __post_init__(self):
        """Validate required fields after initialization."""
        if not self.url or not self.title:
            raise ValueError("URL and title are required")

        # Clean up whitespace
        self.url = self.url.strip()
        self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()
