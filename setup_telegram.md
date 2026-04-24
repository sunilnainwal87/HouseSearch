# Telegram Bot Setup Guide

## Step 1 – Create Your Bot
1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Enter a name (e.g. `HouseSearchBot`)
4. Enter a username ending in `bot` (e.g. `MyHouseSearch_bot`)
5. Copy the token BotFather gives you

## Step 2 – Get Your Chat ID
1. Search for your new bot in Telegram and press **START**
2. Send it any message (e.g. "hello")
3. Visit: `https://api.telegram.org/bot{YOUR_TOKEN}/getUpdates`
4. Find the `"id"` value inside `"chat"` — that is your Chat ID

## Step 3 – Add GitHub Secrets
1. Go to your repo → **Settings → Secrets and variables → Actions**
2. Click **New repository secret** and add:
   - `TELEGRAM_BOT_TOKEN` = your bot token
   - `TELEGRAM_CHAT_ID` = your chat ID number

## Step 4 – Test
Go to **Actions → Daily House Search → Run workflow** to trigger a manual run.
