import json
import os

# Stocké sur le Volume Railway pour survivre aux redéploiements.
BOT_STATE_PATH = os.environ.get("BOT_STATE_PATH", "/data/bot_state.json")
DEFAULT_POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", "90"))
MIN_POLL_INTERVAL = 15


def _load():
    if os.path.exists(BOT_STATE_PATH):
        with open(BOT_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"paused": False, "poll_interval": DEFAULT_POLL_INTERVAL}


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


def get_poll_interval():
    return _load().get("poll_interval", DEFAULT_POLL_INTERVAL)


def set_poll_interval(seconds):
    seconds = max(MIN_POLL_INTERVAL, int(seconds))
    state = _load()
    state["poll_interval"] = seconds
    _save(state)
    return seconds
