# État de l'assistant "ajout de recherche" étape par étape.
# En mémoire seulement : si le bot redémarre en plein milieu, l'utilisateur
# renvoie juste /addsearch pour recommencer (pas grave, pas de perte de données).

_state = {"step": None, "data": {}}


def get_step():
    return _state["step"]


def set_step(step):
    _state["step"] = step


def get_data():
    return _state["data"]


def update_data(key, value):
    _state["data"][key] = value


def reset():
    _state["step"] = None
    _state["data"] = {}
