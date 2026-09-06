import json
import os

# IMPORTANT : sur Railway, monte un Volume et pointe STORAGE_PATH dessus
# (ex: /data/seen_items.json) pour que la liste survive à un redéploiement.
STORAGE_PATH = os.environ.get("STORAGE_PATH", "seen_items.json")


def load_seen():
    if os.path.exists(STORAGE_PATH):
        with open(STORAGE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_seen(data):
    os.makedirs(os.path.dirname(STORAGE_PATH) or ".", exist_ok=True)
    with open(STORAGE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)
