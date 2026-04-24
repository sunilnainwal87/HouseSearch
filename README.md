# 🏡 HouseSearch Agent

An automated daily house search agent for Belgium that scrapes multiple real-estate portals, filters by your criteria, sends **instant Telegram notifications** for new listings, and commits a daily HTML report to this repo.

## 🔍 Search Criteria
- **Locations:** Boortmeerbeek (3190/3191), Steenokkerzeel (1820), Haacht (3150), Zemst (1980), Kortenberg (3070), Mechelen (2800)
- **Type:** Houses only
- **Bedrooms:** ≥ 2
- **Garden:** Required
- **EPC:** A, B, or C only
- **Max Price:** €560,000

## 📡 Sources Scraped
- Immoweb
- Zimmo
- Immoscoop
- Logic-immo
- ERA Belgium
- Remax Belgium
- Heylen Vastgoed
- Dewaele

## ⚙️ Setup

### 1. Create Telegram Bot
See [setup_telegram.md](setup_telegram.md) for step-by-step instructions.

### 2. Add GitHub Secrets
Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram chat/user ID |

### 3. Run Manually (first time)
Go to **Actions → Daily House Search → Run workflow**

## 📅 Schedule
Runs automatically every day at **08:00 Brussels time** (06:00 UTC).

## 📊 Reports
Daily reports are saved in `data/reports/` as HTML and JSON files.

## 🔧 Adjust Filters
Edit `agent/config.py` to change price, EPC, bedrooms, municipalities etc.