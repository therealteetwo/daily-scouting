# CFD Daily Brief

Automated daily intelligence brief for the CFD industry. Pulls industry press RSS,
Google News queries per competitor, and regulator feeds; analyzes everything with the
Claude API using a Bizcuits-specific strategist prompt; delivers to Telegram every
morning via GitHub Actions. Zero infrastructure, ~$1–3/month in API costs.

## Pipeline

```
RSS feeds + Google News queries  →  Claude analysis  →  Telegram
        (fetch.py)                    (analyze.py)      (deliver.py)
```

## Setup (10 minutes)

### 1. Create the Telegram bot
1. Message **@BotFather** on Telegram → `/newbot` → follow prompts.
2. Save the **bot token** it gives you.
3. Message your new bot anything (e.g. "hi") — required before it can message you.
4. Get your **chat ID**: open `https://api.telegram.org/bot<TOKEN>/getUpdates`
   in a browser and copy the `"chat":{"id": ...}` number.

### 2. Get an Anthropic API key
Create one at https://console.anthropic.com → API Keys.

### 3. Create the GitHub repo
1. Push this folder to a new **private** repo.
2. Repo → Settings → Secrets and variables → Actions → add three secrets:
   - `ANTHROPIC_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

### 4. Test it
Actions tab → **CFD Daily Brief** → **Run workflow**. The brief should land in
Telegram within ~2 minutes. Check the run log if not.

After that it runs automatically every day at 05:30 UTC (07:30 Madrid summer time).
Change the time in `.github/workflows/daily-brief.yml` — cron is always UTC.

## Tuning the radar

Everything lives in `config.yaml` — competitors, topic queries, RSS feeds,
lookback window, article cap, model. Edit and push; no code changes needed.

## Run locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=... TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...
python main.py
```

## Notes

- Feeds fail gracefully — one dead source never kills the brief.
- Telegram's 4096-char limit is handled by paragraph-aware chunking.
- Google News RSS is free and needs no API key.
- The API is billed per token; `max_items: 60` in config.yaml caps input cost.
