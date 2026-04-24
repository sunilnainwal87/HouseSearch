"""Entry point: run the full house-search pipeline."""
import json
import logging
import datetime
import requests

from agent.config import (
    FILTERS, DATA_DIR, REPORTS_DIR, LOG_FILE,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
)
from agent.deduplication import load_seen_ids, save_seen_ids, filter_new_listings
from agent.filter import passes_filters
from agent.scrapers.zimmo import ZimmoScraper
from agent.scrapers.logic_immo import LogicImmoScraper
from agent.scrapers.local_agencies import HeylenScraper, DewaeleScraper

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
def send_telegram(listing: dict) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not set – skipping notification")
        return
    price = f"€{listing['price']:,}" if listing.get("price") else "?"
    beds = listing.get("bedrooms") or "?"
    epc = listing.get("epc") or "?"
    garden = "✅" if listing.get("has_garden") else "❓"
    text = (
        f"🏡 *New listing* — {listing.get('source', '').upper()}\n"
        f"📍 {listing.get('municipality', '')} {listing.get('postal_code', '')}\n"
        f"💶 {price}  🛏 {beds} beds  🌿 Garden {garden}  🔋 EPC {epc}\n"
        f"📝 {listing.get('title', '')}\n"
        f"🔗 {listing.get('url', '')}"
    )
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"},
            timeout=15,
        )
        if not resp.ok:
            logger.warning("Telegram error: %s", resp.text)
    except Exception as exc:
        logger.error("Telegram send failed: %s", exc)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------
def save_report(listings: list, all_listings: list) -> None:
    today = datetime.date.today().isoformat()
    # JSON
    json_path = REPORTS_DIR / f"report_{today}.json"
    json_path.write_text(
        json.dumps({"date": today, "new_count": len(listings), "listings": listings}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    # HTML
    rows = ""
    for l in all_listings:
        is_new = l in listings
        badge = '<span style="color:green;font-weight:bold"> NEW</span>' if is_new else ""
        price = f"€{l['price']:,}" if l.get("price") else "—"
        rows += (
            f"<tr>"
            f"<td><a href='{l.get('url','')}' target='_blank'>{l.get('title','')}</a>{badge}</td>"
            f"<td>{l.get('source','')}</td>"
            f"<td>{l.get('municipality','')} {l.get('postal_code','')}</td>"
            f"<td>{price}</td>"
            f"<td>{l.get('bedrooms','?')}</td>"
            f"<td>{'✅' if l.get('has_garden') else '—'}</td>"
            f"<td>{l.get('epc','?')}</td>"
            f"</tr>\n"
        )
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>HouseSearch {today}</title>
<style>body{{font-family:sans-serif;}} table{{border-collapse:collapse;width:100%}} td,th{{border:1px solid #ccc;padding:6px 8px;}} tr:nth-child(even){{background:#f9f9f9}}</style>
</head>
<body>
<h1>🏡 HouseSearch — {today}</h1>
<p>{len(all_listings)} listings found, <strong>{len(listings)} new</strong></p>
<table>
<thead><tr><th>Title</th><th>Source</th><th>Location</th><th>Price</th><th>Beds</th><th>Garden</th><th>EPC</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</body></html>"""
    html_path = REPORTS_DIR / f"report_{today}.html"
    html_path.write_text(html, encoding="utf-8")
    logger.info("Reports saved: %s, %s", json_path.name, html_path.name)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    logger.info("=== HouseSearch agent starting ===")

    scrapers = [ZimmoScraper(), LogicImmoScraper(), HeylenScraper(), DewaeleScraper()]
    all_raw: list = []
    for scraper in scrapers:
        all_raw.extend(scraper.scrape())

    # Apply filters
    filtered = [l for l in all_raw if passes_filters(l, FILTERS)]
    logger.info("%d listings pass filters (out of %d raw)", len(filtered), len(all_raw))

    # Deduplication
    seen_ids = load_seen_ids()
    new_listings = filter_new_listings(filtered, seen_ids)

    # Notifications
    for listing in new_listings:
        send_telegram(listing)

    # Persist
    new_ids = {l["id"] for l in new_listings if l.get("id")}
    save_seen_ids(seen_ids | new_ids)
    save_report(new_listings, filtered)

    logger.info("=== HouseSearch agent done: %d new listings ===", len(new_listings))


if __name__ == "__main__":
    main()
