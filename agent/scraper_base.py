"""Base scraper class and shared helpers."""
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


def empty_listing() -> dict:
    """Return a blank listing dict with all expected keys."""
    return {
        "id": None,
        "source": None,
        "url": None,
        "title": "",
        "description": "",
        "price": None,
        "bedrooms": None,
        "has_garden": None,
        "epc": None,
        "municipality": None,
        "postal_code": None,
        "agency": None,
        "images": [],
    }


class BaseScraper(ABC):
    SOURCE: str = "unknown"

    def scrape(self) -> list:
        try:
            listings = self._scrape()
            logger.info("[%s] scraped %d listings", self.SOURCE, len(listings))
            return listings
        except Exception as exc:
            logger.error("[%s] scraper failed: %s", self.SOURCE, exc, exc_info=True)
            return []

    @abstractmethod
    def _scrape(self) -> list:
        """Subclasses implement this to return raw listings."""
