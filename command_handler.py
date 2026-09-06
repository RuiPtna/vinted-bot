from searches_store import load_searches, add_search, remove_search, save_searches
from bot_state import is_paused, set_paused, get_poll_interval, set_poll_interval, MIN_POLL_INTERVAL

HELP_TEXT = (
    "Commandes disponibles :\n\n"
    "/menu — panneau de contrôle avec boutons\n"
    "/addsearch\n"
    "nom: <nom de la recherche>\n"
    "recherche: <mots-clés>\n"
    "prix_min: <optionnel>\n"
    "prix_max: <optionnel>\n"
    "exclure: <mots séparés par des virgules, optionnel>\n"
    "sauf: <mots séparés par des virgules, optionnel>\n\n"
    "/list — recherches actives (numérotées)\n"
    "/remove <numéro ou nom> — supprime une recherche\n"
    "/clear — supprime toutes les recherches\n"
    "/setinterval <secondes> — change la fréquence de vérification\n"
    "/help — affiche ce message"
)


def parse_fields(lines):
    fields = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip().lower()] = value.strip()
    return fields


def parse_word_list(value):
    return [w.strip() for w in value.split(",") if w.strip()]


def format_search_list(searches):
    lines_out = []
    for i, s in enumerate(searches, start=1):
        details = s.get("search_text", "")
        if s.get("price_from"):
            details += f", min {s['price_from']}€"
        if s.get("price_to"):
            details += f", max {s['price_to']}€"
        if s.get("exclude_words"):
            details += f" | exclut: {', '.join(s['exclude_words'])}"
        if s.get("override_words"):
            details += f" | sauf: {', '.join(s['override_words'])}"
        lines_out.append(f"{i}. {s['name']} — {details}")
    return lines_out


def build_menu_text_and_keyboard():
    paused = is_paused()
    status = "⏸️ En pause" if paused else "▶️ Actif"
    interval = get_poll_interval()
    nb_searches = len(load_searches())

    text = (
        f"Statut : {status}\n"
        f"Intervalle de vérification : {interval}s\n"
        f"Recherches actives : {nb_searches}"
    )

    keyboard = [
        [
            {"text": "⏸️ Arrêter", "callback_data": "pause"},
            {"text": "▶️ Reprendre", "callback_data": "resume"},
        ],
        [
            {"text": "➖ 30s", "callback_data": "interval_dec"},
            {"text": f"⏱ {interval}s", "callback_data": "noop"},
            {"text": "➕ 30s", "callback_data": "interval_inc"},
        ],
        [
            {"text": "📋 Mes recherches", "callback_data": "list"},
            {"text": "❓ Aide", "callback_data": "help"},
        ],
    ]
    return text, keyboard


def handle_callback(data):
    """Traite un clic sur un bouton du /menu. Retourne un message à envoyer en plus (ou None)."""
    if data == "pause":
        set_paused(True)
    elif data == "resume":
        set_paused(False)
    elif data == "interval_dec":
        set_poll_interval(max(MIN_POLL_INTERVAL, get_poll_interval() - 30))
    elif data == "interval_inc":
        set_poll_interval(get_poll_interval() + 30)
    elif data == "list":
        searches = load_searches()
        if not searches:
            return "Aucune recherche configurée."
        return "Recherches actives :\n" + "\n".join(format_search_list(searches))
    elif data == "help":
        return HELP_TEXT
    return None


def handle_message(text):
    text = text.strip()
    lines = text.splitlines()
    if not lines:
        return None
    command = lines[0].strip().lower()

    if command.startswith("/addsearch"):
        fields = parse_fields(lines[1:])
        name = fields.get("nom")
        search_text = fields.get("recherche")
        if not name or not search_text:
            return "Format incorrect. Envoie /help pour voir le format attendu."

        new_search = {"name": name, "search_text": search_text}
        if fields.get("prix_min"):
            new_search["price_from"] = fields["prix_min"]
        if fields.get("prix_max"):
            new_search["price_to"] = fields["prix_max"]
        if fields.get("exclure"):
            new_search["exclude_words"] = parse_word_list(fields["exclure"])
        if fields.get("sauf"):
            new_search["override_words"] = parse_word_list(fields["sauf"])

        add_search(new_search)
        return f"✅ Recherche « {name} » ajoutée."

    if command.startswith("/list"):
        searches = load_searches()
        if not searches:
            return "Aucune recherche configurée."
        return "Recherches actives :\n" + "\n".join(format_search_list(searches))

    if command.startswith("/clear"):
        save_searches([])
        return "🗑️ Toutes les recherches ont été supprimées."

    if command.startswith("/remove"):
        arg = text[len("/remove"):].strip()
        if not arg:
            return "Utilisation : /remove <numéro ou nom> (voir /list)"

        searches = load_searches()
        if arg.isdigit():
            index = int(arg) - 1
            if 0 <= index < len(searches):
                removed_name = searches[index]["name"]
                del searches[index]
                save_searches(searches)
                return f"🗑️ « {removed_name} » supprimée."
            return f"Aucune recherche avec le numéro {arg}. Envoie /list pour voir les numéros actuels."

        removed = remove_search(arg)
        return f"🗑️ « {arg} » supprimée." if removed else f"Aucune recherche nommée « {arg} »."

    if command.startswith("/setinterval"):
        arg = text[len("/setinterval"):].strip()
        if not arg.isdigit():
            return f"Utilisation : /setinterval <secondes> (minimum {MIN_POLL_INTERVAL}s)"
        new_value = set_poll_interval(int(arg))
        return f"⏱ Intervalle réglé sur {new_value}s."

    if command.startswith("/pause"):
        set_paused(True)
        return "⏸️ Bot mis en pause. Aucune recherche ne sera lancée tant que tu n'envoies pas /resume."

    if command.startswith("/resume"):
        set_paused(False)
        return "▶️ Bot relancé, les recherches reprennent."

    if command.startswith("/help") or command.startswith("/start"):
        return HELP_TEXT

    return None
