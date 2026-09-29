import time

from telegram_notify import (
    get_updates,
    send_telegram_message,
    send_message_with_keyboard,
    edit_message_keyboard,
    answer_callback_query,
)
from command_handler import handle_message, handle_callback, build_menu_text_and_keyboard
from searches_store import add_search
import conversation_state as wizard

WIZARD_QUESTIONS = {
    "name": "Comment veux-tu appeler cette recherche ? (ex: PSP)",
    "keywords": "Quels mots-clés chercher sur Vinted ? (ex: psp)",
    "price": "Prix maximum ? Envoie un nombre, ou « skip » pour ne pas filtrer.",
    "category": (
        "ID de catégorie Vinted, optionnel — envoie le nombre, ou « skip ».\n"
        "Pour le trouver : sur vinted.fr, filtre par cette catégorie, regarde "
        "catalog[]=XXXX dans l'URL."
    ),
}
SKIP_WORDS = ("skip", "non", "aucun", "-", "passer")


def start_wizard():
    wizard.reset()
    wizard.set_step("name")
    return WIZARD_QUESTIONS["name"]


def handle_wizard_answer(text):
    step = wizard.get_step()
    text = text.strip()

    if text.lower() in ("/annuler", "annuler", "/cancel"):
        wizard.reset()
        return "❌ Ajout annulé."

    if step == "name":
        wizard.update_data("name", text)
        wizard.set_step("keywords")
        return WIZARD_QUESTIONS["keywords"]

    if step == "keywords":
        wizard.update_data("search_text", text)
        wizard.set_step("price")
        return WIZARD_QUESTIONS["price"]

    if step == "price":
        if text.lower() not in SKIP_WORDS:
            if not text.isdigit():
                return "Envoie un nombre (ex: 60), ou « skip »."
            wizard.update_data("price_to", text)
        wizard.set_step("category")
        return WIZARD_QUESTIONS["category"]

    if step == "category":
        if text.lower() not in SKIP_WORDS:
            if not text.isdigit():
                return "Envoie un nombre (l'ID de catégorie), ou « skip »."
            wizard.update_data("catalog_ids", text)

        data = wizard.get_data()
        add_search(data)
        wizard.reset()
        return f"✅ Recherche « {data['name']} » ajoutée. Envoie /menu pour la voir."

    wizard.reset()
    return None


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
                    if data == "addsearch":
                        answer_callback_query(callback["id"])
                        send_telegram_message(start_wizard())
                        continue

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
                # Si l'assistant pas-à-pas est en cours, on traite la réponse en priorité
                if wizard.get_step() is not None:
                    response = handle_wizard_answer(text)
                    if response:
                        send_telegram_message(response)
                    continue

                if text.strip().lower().startswith("/menu"):
                    menu_text, keyboard = build_menu_text_and_keyboard()
                    send_message_with_keyboard(menu_text, keyboard)
                    continue

                # /addsearch tout seul (sans les champs nom:/recherche:...) -> assistant
                if text.strip().lower() == "/addsearch":
                    send_telegram_message(start_wizard())
                    continue

                response = handle_message(text)
                if response:
                    send_telegram_message(response)
            except Exception as e:
                print(f"[commandes] erreur traitement : {e}")
