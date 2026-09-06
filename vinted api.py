import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


class VintedClient:
    """
    Petit client pour l'API non-officielle de Vinted.
    Vinted protège son API avec Datadome : il faut d'abord visiter le site
    pour récupérer des cookies valides avant d'appeler l'API JSON.
    """

    def __init__(self, domain="vinted.fr"):
        self.domain = domain
        self.base_url = f"https://www.{domain}"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
        })
        self._refresh_session()

    def _refresh_session(self):
        self.session.get(self.base_url, timeout=15)

    def search(self, params, retry=True):
        url = f"{self.base_url}/api/v2/catalog/items"
        resp = self.session.get(url, params=params, timeout=15)

        if resp.status_code in (401, 403) and retry:
            # Cookies expirés / bloqués -> on rafraîchit et on réessaie une fois
            self._refresh_session()
            return self.search(params, retry=False)

        resp.raise_for_status()
        return resp.json().get("items", [])
