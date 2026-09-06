# Bot Telegram — Alertes Vinted

Surveille plusieurs recherches Vinted en continu et envoie une notification
Telegram dès qu'une nouvelle annonce correspond à tes critères.

## 1. Créer le bot Telegram

1. Ouvre Telegram, cherche **@BotFather**, envoie `/newbot` et suis les
   instructions. Tu obtiens un **token** (ex: `123456:ABC-DEF...`).
2. Envoie un message à ton nouveau bot (n'importe quoi), puis va sur
   `https://api.telegram.org/bot<TON_TOKEN>/getUpdates` dans un navigateur.
   Tu trouveras ton **chat_id** dans le JSON retourné (`"chat":{"id": ...}`).

## 2. Configurer tes recherches

Édite `searches.json`. Chaque entrée est une recherche indépendante :

```json
{
  "name": "Doudoune Nike",
  "search_text": "doudoune nike",
  "price_from": 0,
  "price_to": 40
}
```

Champs optionnels supportés : `search_text`, `price_from`, `price_to`,
`catalog_ids`, `brand_ids`, `size_ids` (ces derniers sont des IDs numériques
Vinted — tu peux les récupérer en faisant une recherche sur vinted.fr et en
regardant l'URL générée, ou l'onglet Réseau du navigateur).

## 3. Déployer sur Railway

1. Crée un nouveau projet Railway → **Deploy from GitHub repo** (pousse ce
   dossier sur un repo GitHub) ou **Empty Project** puis upload les fichiers.
2. Dans **Variables**, ajoute :
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `STORAGE_PATH` = `/data/seen_items.json`
   - `POLL_INTERVAL` = `90` (secondes entre deux vérifications, à ne pas
     descendre trop bas pour éviter un blocage par Vinted)
3. **Ajoute un Volume** (Settings → Volumes) et monte-le sur `/data`. C'est
   important : sans ça, si Railway redéploie ton service, la liste des
   annonces déjà vues repart de zéro et tu reçois un pic de doublons.
4. Vérifie que la commande de démarrage est `python main.py` (le `Procfile`
   s'en charge normalement).
5. Déploie. Dans les logs tu dois voir `Bot Vinted démarré.`

## Limites à connaître

- L'API utilisée est **non officielle** (reverse-engineered) : Vinted peut la
  modifier ou bloquer les requêtes automatisées à tout moment. Un
  `POLL_INTERVAL` trop bas augmente le risque de blocage (Datadome).
- Rien n'automatise l'achat : le bot t'envoie juste le lien, tu achètes
  toi-même en un clic depuis Telegram.
