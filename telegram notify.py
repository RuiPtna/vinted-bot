import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": False,
        },
        timeout=15,
    )
    resp.raise_for_status()
