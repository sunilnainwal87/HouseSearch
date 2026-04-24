"""
Logic-immo.be scraper.
"""
import logging
import re
import time
import requests
from bs4 import BeautifulSoup
from agent.scraper_base import BaseScraper, empty_listing
from agent.config import MUNICIPALITIES, FILTERS

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "nl-BE,nl;q=0.9",
}


class LogicImmoScraper(BaseScraper):
    SOURCE = "logic-immo"

    def _scrape(self) -> list:
        results = []
        for muni in MUNICIPALITIES:
            results.extend(self._scrape_muni(muni["postal"], muni["name"]))
            time.sleep(2)
        return results

    def _scrape_muni(self, postal: str, name: str) -> list:
        listings = []
        url = (
            f"https://www.logic-immo.be/search-results"
            f"?transactionType=buy&propertyType=house"
            f"&postalCode={postal}&maxPrice={FILTERS['max_price']}"
            f"&minBedrooms={FILTERS['min_bedrooms']}"
        )
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if not resp.ok:
                logger.warning(f"[logic-immo] HTTP {resp.status_code} for {postal}")
                return []
            soup = BeautifulSoup(resp.text, "lxml")
            cards = soup.select(".property-card, .classified-card, [class*='property'], [class*='listing']")
            for card in cards:
                listing = empty_listing()
                listing["source"] = self.SOURCE
                listing["municipality"] = name
                listing["postal_code"] = postal
                link = card.select_one("a[href]")
                href = link["href"] if link else ""
                if href and not href.startswith("http"):
                    href = "https://www.logic-immo.be" + href
                listing["url"] = href
                listing["id"] = f"logicimmo_{re.sub(r'[^a-zA-Z0-9]', '_', href)[-60:]}"
                price_el = card.select_one(".price, [class*='price']")
                if price_el:
                    digits = re.sub(r"[^0-9]", "", price_el.get_text())
                    listing["price"] = int(digits) if digits else None
                title_el = card.select_one("h2, h3, [class*='title']")
                listing["title"] = title_el.get_text(strip=True) if title_el else ""
                desc = card.get_text(separator=" ", strip=True).lower()
                if any(w in desc for w in ["tuin", "garden", "jardin"]):
                    listing["has_garden"] = True
                listings.append(listing)
        except Exception as e:
            logger.error(f"[logic-immo] error for {postal}: {e}", exc_info=True)
        logger.info(f"[logic-immo] {len(listings)} for {postal}")
        return listings