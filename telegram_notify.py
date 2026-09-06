import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_telegram_message(text):
    resp = requests.post(
        f"{API_URL}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": False,
        },
        timeout=15,
    )
    resp.raise_for_status()


def send_message_with_keyboard(text, keyboard):
    resp = requests.post(
        f"{API_URL}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "reply_markup": {"inline_keyboard": keyboard},
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["result"]


def edit_message_keyboard(message_id, text, keyboard):
    resp = requests.post(
        f"{API_URL}/editMessageText",
        json={
            "chat_id": CHAT_ID,
            "message_id": message_id,
            "text": text,
            "reply_markup": {"inline_keyboard": keyboard},
        },
        timeout=15,
    )
    resp.raise_for_status()


def answer_callback_query(callback_query_id, text=None):
    data = {"callback_query_id": callback_query_id}
    if text:
        data["text"] = text
    requests.post(f"{API_URL}/answerCallbackQuery", data=data, timeout=15)


def get_updates(offset=None, timeout=25):
    params = {"timeout": timeout, "allowed_updates": ["message", "callback_query"]}
    if offset is not None:
        params["offset"] = offset
    resp = requests.get(f"{API_URL}/getUpdates", params=params, timeout=timeout + 10)
    resp.raise_for_status()
    return resp.json().get("result", [])


def send_photo_with_keyboard(photo_url, caption, keyboard):
    resp = requests.post(
        f"{API_URL}/sendPhoto",
        json={
            "chat_id": CHAT_ID,
            "photo": photo_url,
            "caption": caption,
            "reply_markup": {"inline_keyboard": keyboard},
        },
        timeout=15,
    )
    resp.raise_for_status()
