"""Deliver the brief to Telegram, handling the 4096-char message limit."""

import os

import requests

API = "https://api.telegram.org/bot{token}/sendMessage"
LIMIT = 4000  # margin under Telegram's 4096 hard limit


def _chunks(text):
    """Split on paragraph boundaries so sections stay intact."""
    if len(text) <= LIMIT:
        return [text]
    parts, current = [], ""
    for para in text.split("\n\n"):
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) > LIMIT:
            if current:
                parts.append(current)
            current = para[:LIMIT]  # single paragraph too long: hard cut
        else:
            current = candidate
    if current:
        parts.append(current)
    return parts


def send(text):
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    url = API.format(token=token)

    for chunk in _chunks(text):
        r = requests.post(url, json={
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }, timeout=30)
        if r.status_code != 200:
            # HTML parse errors are the usual culprit — retry as plain text
            print(f"[warn] HTML send failed ({r.text[:200]}), retrying plain")
            r = requests.post(url, json={
                "chat_id": chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            }, timeout=30)
        r.raise_for_status()
    print("[info] delivered to Telegram")
