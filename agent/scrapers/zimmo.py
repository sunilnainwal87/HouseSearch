"""
Zimmo.be scraper (HTML parsing).
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
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "nl-BE,nl;q=0.9",
}

def parse_price(text: str):
    digits = re.sub(r"[^0-9]", "", text or "")
    return int(digits) if digits else None


class ZimmoScraper(BaseScraper):
    SOURCE = "zimmo"

    def _scrape(self) -> list:
        results = []
        for muni in MUNICIPALITIES:
            results.extend(self._scrape_muni(muni["name"], muni["postal"]))
            time.sleep(2)
        return results

    def _scrape_muni(self, name: str, postal: str) -> list:
        listings = []
        url = (
            f"https://www.zimmo.be/nl/{name}-{postal}/te-koop/huis/"
            f"?filter=price:max:{FILTERS['max_price']},bedrooms:min:{FILTERS['min_bedrooms']}"
        )
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if not resp.ok:
                logger.warning(f"[zimmo] HTTP {resp.status_code} for {name}")
                return []
            soup = BeautifulSoup(resp.text, "lxml")
            cards = soup.select(".property-item, .listing-card, [data-listing-id], .c-card")
            for card in cards:
                listing = empty_listing()
                listing["source"] = self.SOURCE
                listing["municipality"] = name
                listing["postal_code"] = postal
                link = card.select_one("a[href]")
                href = link["href"] if link else ""
                if href and not href.startswith("http"):
                    href = "https://www.zimmo.be" + href
                listing["url"] = href
                listing["id"] = f"zimmo_{re.sub(r'[^a-zA-Z0-9]', '_', href)[-60:]}'"
                price_el = card.select_one(".price, .c-price, [class*='price']")
                listing["price"] = parse_price(price_el.get_text()) if price_el else None
                beds_el = card.select_one("[class*='bedroom'], [class*='bed']")
                if beds_el:
                    m = re.search(r"(\d+)", beds_el.get_text())
                    listing["bedrooms"] = int(m.group(1)) if m else None
                epc_el = card.select_one(".epc-badge, [class*='epc'], [class*='energy']")
                if epc_el:
                    m = re.search(r"[ABCDEFG][+]*", epc_el.get_text(strip=True).upper())
                    listing["epc"] = m.group(0) if m else None
                title_el = card.select_one("h2, h3, .title, [class*='title']")
                listing["title"] = title_el.get_text(strip=True) if title_el else ""
                desc = card.get_text(separator=" ", strip=True).lower()
                listing["has_garden"] = any(w in desc for w in ["tuin", "garden", "jardin"])
                img = card.select_one("img")
                if img and img.get("src"):
                    listing["images"] = [img["src"]]
                listings.append(listing)
        except Exception as e:
            logger.error(f"[zimmo] error for {name}: {e}", exc_info=True)
        logger.info(f"[zimmo] {len(listings)} listings for {name}")
        return listings
