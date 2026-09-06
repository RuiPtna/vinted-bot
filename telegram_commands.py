import time

from telegram_notify import (
    get_updates,
    send_telegram_message,
    send_message_with_keyboard,
    edit_message_keyboard,
    answer_callback_query,
)
from command_handler import handle_message, handle_callback, build_menu_text_and_keyboard


def listen_for_commands():
    offset = None
    while True:
        try:
            updates = get_updates(offset=offset)
        except Exception as e:
            print(f"[commandes] erreur getUpdates : {e}")
            time.sleep(5)
            continue

        for update in updates:
            offset = update["update_id"] + 1

            callback = update.get("callback_query")
            if callback:
                data = callback.get("data", "")
                message = callback.get("message", {})

                try:
                    extra_response = handle_callback(data)

                    if data != "noop":
                        text, keyboard = build_menu_text_and_keyboard()
                        if "message_id" in message:
                            edit_message_keyboard(message["message_id"], text, keyboard)

                    answer_callback_query(callback["id"])

                    if extra_response:
                        send_telegram_message(extra_response)
                except Exception as e:
                    print(f"[commandes] erreur callback : {e}")
                continue

            message = update.get("message", {})
            text = message.get("text")
            if not text:
                continue

            try:
                if text.strip().lower().startswith("/menu"):
                    menu_text, keyboard = build_menu_text_and_keyboard()
                    send_message_with_keyboard(menu_text, keyboard)
                    continue

                response = handle_message(text)
                if response:
                    send_telegram_message(response)
            except Exception as e:
                print(f"[commandes] erreur traitement : {e}")
