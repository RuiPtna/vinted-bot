import json
import os

# Stocké sur le Volume Railway (/data) pour survivre aux redéploiements.
SEARCHES_STORAGE_PATH = os.environ.get("SEARCHES_STORAGE_PATH", "/data/searches.json")
DEFAULT_SEARCHES_FILE = os.environ.get("SEARCHES_FILE", "searches.json")


def load_searches():
    if os.path.exists(SEARCHES_STORAGE_PATH):
        with open(SEARCHES_STORAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    # Premier démarrage : on part des recherches livrées avec le code
    if os.path.exists(DEFAULT_SEARCHES_FILE):
        with open(DEFAULT_SEARCHES_FILE, "r", encoding="utf-8") as f:
            searches = json.load(f)
        save_searches(searches)
        return searches

    return []


def save_searches(searches):
    os.makedirs(os.path.dirname(SEARCHES_STORAGE_PATH) or ".", exist_ok=True)
    with open(SEARCHES_STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(searches, f, ensure_ascii=False, indent=2)


def add_search(new_search):
    searches = load_searches()
    searches = [s for s in searches if s["name"].lower() != new_search["name"].lower()]
    searches.append(new_search)
    save_searches(searches)
    return searches


def remove_search(name):
    searches = load_searches()
    filtered = [s for s in searches if s["name"].lower() != name.lower()]
    removed = len(filtered) != len(searches)
    save_searches(filtered)
    return removed
