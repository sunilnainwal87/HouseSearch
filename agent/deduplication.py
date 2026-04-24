"""Track seen listing IDs to avoid duplicate Telegram notifications."""
import json
import logging
from agent.config import SEEN_LISTINGS_FILE

logger = logging.getLogger(__name__)

def load_seen_ids() -> set:
    if SEEN_LISTINGS_FILE.exists():
        try:
            data = json.loads(SEEN_LISTINGS_FILE.read_text(encoding="utf-8"))
            return set(data.get("seen_ids", []))
        except Exception as exc:
            logger.warning("Could not load seen_listings.json: %s", exc)
    return set()

def save_seen_ids(seen_ids: set) -> None:
    SEEN_LISTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SEEN_LISTINGS_FILE.write_text(
        json.dumps({"seen_ids": sorted(seen_ids)}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Saved %d seen listing IDs", len(seen_ids))

def filter_new_listings(listings: list, seen_ids: set) -> list:
    new = [l for l in listings if l["id"] and l["id"] not in seen_ids]
    logger.info("%d new listings out of %d total", len(new), len(listings))
    return new