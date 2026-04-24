"""
Configuration for the HouseSearch agent.
Edit this file to change your search criteria.
"""
import os
import pathlib

MUNICIPALITIES = [
    {"name": "boortmeerbeek", "postal": "3190"},
    {"name": "hever",         "postal": "3191"},
    {"name": "steenokkerzeel","postal": "1820"},
    {"name": "haacht",        "postal": "3150"},
    {"name": "zemst",         "postal": "1980"},
    {"name": "kortenberg",    "postal": "3070"},
    {"name": "mechelen",      "postal": "2800"},
]

FILTERS = {
    "max_price": 560000,
    "min_bedrooms": 2,
    "require_garden": True,
    "allowed_epc": ["A", "A+", "A++", "B", "C"],
    "property_type": "house",
}

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

ROOT_DIR           = pathlib.Path(__file__).parent.parent
DATA_DIR           = ROOT_DIR / "data"
REPORTS_DIR        = DATA_DIR / "reports"
SEEN_LISTINGS_FILE = DATA_DIR / "seen_listings.json"
LOG_FILE           = DATA_DIR / "search.log"
