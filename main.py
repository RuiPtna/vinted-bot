import os
import random
import threading
import time

from vinted_api import VintedClient
from telegram_notify import send_telegram_message, send_message_with_keyboard, send_photo_with_keyboard
from telegram_commands import listen_for_commands
from searches_store import load_searches
from storage import load_seen, save_seen
from bot_state import is_paused

POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "90"))
MAX_SEEN_PER_SEARCH = 500


def build_params(search):
    params = {"per_page": 20, "order": "newest_first"}
    for key in ("search_text", "price_from", "price_to", "catalog_ids", "brand_ids", "size_ids"):
        if search.get(key):
            params[key] = search[key]
    return params


def format_message(search_name, item):
    title = item.get("title", "Sans titre")
    price = item.get("price", {})
    if isinstance(price, dict):
        amount = price.get("amount")
        currency = price.get("currency_code", "")
    else:
        amount, currency = price, ""
    return f"🔎 {search_name}\n{title}\n💶 {amount} {currency}"


def run_cycle(client, seen):
    for search in load_searches():
        name = search.get("name", "recherche")
        seen_ids = set(seen.get(name, []))

        try:
            items = client.search(build_params(search))
        except Exception as e:
            print(f"[{name}] erreur recherche : {e}")
            continue

        new_items = [it for it in items if str(it["id"]) not in seen_ids]

        for item in reversed(new_items):  # du plus ancien au plus récent
            try:
                url = item.get("url", "")
                text = format_message(name, item)
                keyboard = [[{"text": "🔗 Ouvrir sur Vinted", "url": url}]] if url else None

                photo = item.get("photo")
                photo_url = photo.get("url") if isinstance(photo, dict) else None

                if photo_url and keyboard:
                    send_photo_with_keyboard(photo_url, text, keyboard)
                elif keyboard:
                    send_message_with_keyboard(text, keyboard)
                else:
                    send_telegram_message(text)
            except Exception as e:
                print(f"[{name}] erreur envoi Telegram : {e}")
            seen_ids.add(str(item["id"]))
            time.sleep(1)

        seen[name] = list(seen_ids)[-MAX_SEEN_PER_SEARCH:]
        save_seen(seen)

        time.sleep(random.uniform(2, 5))  # petite pause entre chaque recherche


def main():
    client = VintedClient()
    seen = load_seen()

    # Écoute des commandes (/addsearch, /list, /remove...) en tâche de fond
    threading.Thread(target=listen_for_commands, daemon=True).start()

    print("Bot Vinted démarré.")
    while True:
        if is_paused():
            print("Bot en pause.")
        else:
            run_cycle(client, seen)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
