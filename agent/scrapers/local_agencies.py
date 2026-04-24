"""
Local agency scrapers: Heylen Vastgoed, Dewaele.
"""
import logging
import re
import time
import requests
from bs4 import BeautifulSoup
from agent.scraper_base import BaseScraper, empty_listing
from agent.config import FILTERS

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "nl-BE,nl;q=0.9",
}


class HeylenScraper(BaseScraper):
    SOURCE = "heylen"
    REGIONS = ["boortmeerbeek", "steenokkerzeel", "haacht", "zemst", "kortenberg", "mechelen"]

    def _scrape(self) -> list:
        listings = []
        for region in self.REGIONS:
            url = f"https://www.heylen.be/nl/te-koop?type=huis&regio={region}&maxprijs={FILTERS['max_price']}"
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
                if not resp.ok:
                    logger.warning(f"[heylen] HTTP {resp.status_code} for {region}")
                    continue
                soup = BeautifulSoup(resp.text, "lxml")
                cards = soup.select(".property-card, .listing, [class*='property'], [class*='pand']")
                for card in cards:
                    listing = empty_listing()
                    listing["source"] = self.SOURCE
                    listing["municipality"] = region
                    listing["agency"] = "Heylen Vastgoed"
                    link = card.select_one("a[href]")
                    href = link["href"] if link else ""
                    if href and not href.startswith("http"):
                        href = "https://www.heylen.be" + href
                    listing["url"] = href
                    listing["id"] = f"heylen_{re.sub(r'[^a-zA-Z0-9]', '_', href)[-60:]}"
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
                time.sleep(1.5)
            except Exception as e:
                logger.error(f"[heylen] error for {region}: {e}", exc_info=True)
        logger.info(f"[heylen] {len(listings)} total listings")
        return listings


class DewaeleScraper(BaseScraper):
    SOURCE = "dewaele"
    POSTALS = ["3190", "3191", "1820", "3150", "1980", "3070", "2800"]

    def _scrape(self) -> list:
        listings = []
        for postal in self.POSTALS:
            url = f"https://www.dewaele.com/nl/te-koop?types=huis&maxPrice={FILTERS['max_price']}&q={postal}"
            try:
                resp = requests.get(url, headers=HEADERS, timeout=20)
                if not resp.ok:
                    logger.warning(f"[dewaele] HTTP {resp.status_code} for {postal}")
                    continue
                soup = BeautifulSoup(resp.text, "lxml")
                cards = soup.select(".property-card, .listing, [class*='property'], [class*='pand']")
                for card in cards:
                    listing = empty_listing()
                    listing["source"] = self.SOURCE
                    listing["postal_code"] = postal
                    listing["agency"] = "Dewaele"
                    link = card.select_one("a[href]")
                    href = link["href"] if link else ""
                    if href and not href.startswith("http"):
                        href = "https://www.dewaele.com" + href
                    listing["url"] = href
                    listing["id"] = f"dewaele_{re.sub(r'[^a-zA-Z0-9]', '_', href)[-60:]}"
                    price_el = card.select_one(".price, [class*='price']")
                    if price_el:
                        digits = re.sub(r"[^0-9]", "", price_el.get_text())
                        listing["price"] = int(digits) if digits else None
                    title_el = card.select_one("h2, h3, [class*='title']")
                    listing["title"] = title_el.get_text(strip=True) if title_el else ""
                    listings.append(listing)
                time.sleep(1.5)
            except Exception as e:
                logger.error(f"[dewaele] error for {postal}: {e}", exc_info=True)
        logger.info(f"[dewaele] {len(listings)} total listings")
        return listings
