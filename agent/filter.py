"""Apply hard filters to raw listings."""
import logging

logger = logging.getLogger(__name__)

GARDEN_KEYWORDS = ["tuin", "garden", "jardin", "terras met tuin", "privatieve tuin"]
ALLOWED_EPC = {"A", "A+", "A++", "B", "C"}

def passes_filters(listing: dict, filters: dict) -> bool:
    """Return True only if listing meets ALL hard filters."""
    # --- Price ---
    price = listing.get("price")
    if price is not None and price > filters["max_price"]:
        return False

    # --- Bedrooms ---
    beds = listing.get("bedrooms")
    if beds is not None and beds < filters["min_bedrooms"]:
        return False

    # --- Garden ---
    if filters.get("require_garden"):
        has_garden = listing.get("has_garden")
        if not has_garden:
            text = (listing.get("description", "") + " " + listing.get("title", "")).lower()
            if not any(kw in text for kw in GARDEN_KEYWORDS):
                return False

    # --- EPC (if known, must be A/B/C) ---
    epc = (listing.get("epc") or "").strip().upper()
    if epc and epc not in ALLOWED_EPC:
        return False
    # Unknown EPC: include it (buyer verifies manually)

    return True
