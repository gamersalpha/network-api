
# 🌐 Network API

Une API réseau simple, puissante et extensible, construite avec **FastAPI**, permettant d'exécuter des outils de diagnostic réseau via HTTP (Swagger UI ou requêtes REST).

---

## 🚀 Fonctionnalités

| Endpoint            | Description                                           |
|---------------------|-------------------------------------------------------|
| `GET /v1/ping`      | Vérifie la connectivité d’un hôte                     |
| `GET /v1/dig`       | Résolution DNS détaillée (A, MX, TXT, etc.)           |
| `GET /v1/nslookup`  | Résolution DNS simplifiée                             |
| `GET /v1/whois`     | Informations WHOIS sur un domaine                     |
| `GET /v1/traceroute`| Affiche le chemin réseau jusqu’à une cible           |
| `GET /v1/nmap`      | Scan de ports (top100, complet ou custom)            |
| `GET /v1/dns-full`  | Récupère tous les enregistrements DNS                |

---

## 🔐 Sécurité

Toutes les routes sous `/v1/` sont **protégées par une API Key**.

- L'API attend un header : `X-API-Key`
- Les clés et permissions sont définies dans `.env`

Exemple :
```http
GET /v1/ping?host=8.8.8.8
X-API-Key: votre_cle_api
```

---

## ⚙️ Installation locale

```bash
git clone https://github.com/gamersalpha/network-api.git
cd network-api

python -m venv venv
# Activation
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8088
```

---

## 🐳 Utilisation avec Docker

```bash
docker compose up --build
```

- **Swagger UI** : [http://localhost:8088/docs](http://localhost:8088/docs)  
- **API directe** : `http://localhost:8088/v1/...`

---

## 🧪 Tests unitaires

Lancer les tests :

```bash
pytest -v
```

Avec couverture :

```bash
pytest --cov=app --cov-report=html
```

Ouvre ensuite `htmlcov/index.html` pour voir les lignes couvertes ✅

---

## 📁 Arborescence (extrait)

```
app/
├── api/
│   └── v1/
│       └── endpoints/      # Routes : ping, dig, etc.
├── core/                   # Middleware de sécurité
├── models/                # Schémas de réponse
├── services/              # Logiciel métier
├── main.py                # Point d’entrée
```

---

## 🧭 Roadmap

- [x] Authentification par API Key
- [x] Middleware de sécurité avec logs, rate-limit, validation
- [x] Tests unitaires pour `/ping`
- [ ] Support complet IPv6
- [ ] Export des résultats (JSON brut, CSV, XML)
- [ ] Mode batch (ping / nmap multiple)
- [ ] CI/CD GitHub Actions

---

## 📄 Licence

**MIT** — Libre d’utilisation, modification et contribution.

---

## 👨‍💻 Auteur

- GitHub : [@gamersalpha](https://github.com/gamersalpha)
