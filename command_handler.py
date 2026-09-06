from searches_store import load_searches, add_search, remove_search, save_searches
from bot_state import is_paused, set_paused

HELP_TEXT = (
    "Commandes disponibles :\n\n"
    "/menu — affiche les boutons Arrêter / Reprendre\n"
    "/addsearch\n"
    "nom: <nom de la recherche>\n"
    "recherche: <mots-clés>\n"
    "prix_min: <optionnel>\n"
    "prix_max: <optionnel>\n"
    "exclure: <mots séparés par des virgules, optionnel>\n"
    "sauf: <mots séparés par des virgules, optionnel>\n\n"
    "'exclure' rejette l'annonce si un de ces mots est dans le titre.\n"
    "'sauf' repasse l'annonce même si un mot d'exclusion est présent.\n\n"
    "/list — affiche tes recherches actives (numérotées)\n"
    "/remove <numéro ou nom> — supprime une recherche\n"
    "/clear — supprime toutes les recherches\n"
    "/help — affiche ce message\n\n"
    "Exemple (console PSP, sans les annonces de jeux seuls) :\n"
    "/addsearch\n"
    "nom: PSP\n"
    "recherche: psp\n"
    "prix_max: 60\n"
    "exclure: jeu, jeux, cartouche\n"
    "sauf: console, pack, lot"
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


def build_menu_text_and_keyboard():
    paused = is_paused()
    status = "⏸️ En pause — aucune recherche en cours" if paused else "▶️ Actif — recherche en cours"
    text = f"Statut du bot :\n{status}"
    keyboard = [[
        {"text": "⏸️ Arrêter", "callback_data": "pause"},
        {"text": "▶️ Reprendre", "callback_data": "resume"},
    ]]
    return text, keyboard


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

    if command.startswith("/pause"):
        set_paused(True)
        return "⏸️ Bot mis en pause. Aucune recherche ne sera lancée tant que tu n'envoies pas /resume."

    if command.startswith("/resume"):
        set_paused(False)
        return "▶️ Bot relancé, les recherches reprennent."

    if command.startswith("/help") or command.startswith("/start"):
        return HELP_TEXT

    return None
