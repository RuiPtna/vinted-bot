import json
import os

# Stocké sur le Volume Railway pour survivre aux redéploiements.
BOT_STATE_PATH = os.environ.get("BOT_STATE_PATH", "/data/bot_state.json")


def _load():
    if os.path.exists(BOT_STATE_PATH):
        with open(BOT_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"paused": False}


def _save(state):
    os.makedirs(os.path.dirname(BOT_STATE_PATH) or ".", exist_ok=True)
    with open(BOT_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f)


def is_paused():
    return _load().get("paused", False)


def set_paused(paused):
    state = _load()
    state["paused"] = paused
    _save(state)
