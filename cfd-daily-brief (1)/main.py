"""CFD Daily Brief — fetch industry news, analyze with Claude, deliver to Telegram."""

import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml

from src.analyze import build_brief
from src.deliver import send
from src.fetch import fetch_all


def main():
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    tz = ZoneInfo(config.get("timezone", "UTC"))
    date_str = datetime.now(tz).strftime("%A, %d %B %Y")

    items = fetch_all(config)
    if not items:
        send(f"<b>🎯 CFD DAILY BRIEF — {date_str}</b>\n\nNo items collected in the last "
             "24h. All feeds may be down — check the Actions log.")
        return

    brief = build_brief(items, config, date_str)
    send(brief)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[error] {exc}", file=sys.stderr)
        sys.exit(1)
