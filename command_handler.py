from searches_store import load_searches, add_search, remove_search
from bot_state import is_paused, set_paused

HELP_TEXT = (
    "Commandes disponibles :\n\n"
    "/menu — affiche les boutons Arrêter / Reprendre\n"
    "/addsearch\n"
    "nom: <nom de la recherche>\n"
    "recherche: <mots-clés>\n"
    "prix_min: <optionnel>\n"
    "prix_max: <optionnel>\n\n"
    "/list — affiche tes recherches actives\n"
    "/remove <nom> — supprime une recherche\n"
    "/help — affiche ce message\n\n"
    "Exemple :\n"
    "/addsearch\n"
    "nom: Doudoune Nike\n"
    "recherche: doudoune nike\n"
    "prix_max: 40"
)


def parse_fields(lines):
    fields = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip().lower()] = value.strip()
    return fields


def build_menu_text_and_keyboard():
    paused = is_paused()
    status = "⏸️ En pause — aucune recherche en cours" if paused else "▶️ Actif — recherche en cours"
    text = f"Statut du bot :\n{status}"
    keyboard = [[
        {"text": "⏸️ Arrêter", "callback_data": "pause"},
        {"text": "▶️ Reprendre", "callback_data": "resume"},
    ]]
    return text, keyboard


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

        add_search(new_search)
        return f"✅ Recherche « {name} » ajoutée."

    if command.startswith("/list"):
        searches = load_searches()
        if not searches:
            return "Aucune recherche configurée."
        lines_out = []
        for s in searches:
            details = s.get("search_text", "")
            if s.get("price_from"):
                details += f", min {s['price_from']}€"
            if s.get("price_to"):
                details += f", max {s['price_to']}€"
            lines_out.append(f"• {s['name']} — {details}")
        return "Recherches actives :\n" + "\n".join(lines_out)

    if command.startswith("/remove"):
        name = text[len("/remove"):].strip()
        if not name:
            return "Utilisation : /remove <nom de la recherche>"
        removed = remove_search(name)
        return f"🗑️ « {name} » supprimée." if removed else f"Aucune recherche nommée « {name} »."

    if command.startswith("/pause"):
        set_paused(True)
        return "⏸️ Bot mis en pause. Aucune recherche ne sera lancée tant que tu n'envoies pas /resume."

    if command.startswith("/resume"):
        set_paused(False)
        return "▶️ Bot relancé, les recherches reprennent."

    if command.startswith("/help") or command.startswith("/start"):
        return HELP_TEXT

    return None
