
# 🌐 Network API

Une API réseau simple, puissante et extensible, construite avec **FastAPI**, permettant d'exécuter des outils de diagnostic réseau via HTTP (Swagger UI ou requêtes REST).

---

## 🚀 Fonctionnalités

| Endpoint            | Description                                           | Accès       |
|---------------------|-------------------------------------------------------|-------------|
| `GET /v1/ping`      | Vérifie la connectivité d’un hôte                     | Dev & Admin |
| `GET /v1/dig`       | Résolution DNS détaillée (A, MX, TXT, etc.)           | Dev & Admin |
| `GET /v1/nslookup`  | Résolution DNS simplifiée                             | Dev & Admin |
| `GET /v1/whois`     | Informations WHOIS sur un domaine                     | Dev & Admin |
| `GET /v1/traceroute`| Affiche le chemin réseau jusqu’à une cible           | Dev & Admin |
| `GET /v1/nmap`      | Scan de ports (top100, complet ou custom)            | Admin only  |
| `GET /v1/dns-full`  | Récupère tous les enregistrements DNS                | Dev & Admin |

---

## 🔐 Sécurité

Toutes les routes sous `/v1/` sont **protégées par une API Key** :

- Header requis : `X-API-Key`
- Les clés sont définies dans le fichier `.env`

### 🔑 Exemple `.env`

```env
API_KEY_DEV=dev_key_123456
API_KEY_ADMIN=admin_key_654321
```

### 🔓 Rôles :

- `dev_key_123456` → accès aux outils standards (`ping`, `whois`, etc.)
- `admin_key_654321` → accès complet (y compris `nmap`)

---

## ⚙️ Installation locale

```bash
git clone https://github.com/gamersalpha/network-api.git
cd network-api

python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

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

## 🧪 Tests

Lancer tous les tests :

```bash
pytest -v
```

Tester uniquement le ping :

```bash
pytest tests/test_ping.py -v
```

Tester les protections de sécurité :

```bash
pytest tests/test_security.py -v
```

Avec couverture :

```bash
pytest --cov=app --cov-report=html
```

---

## 📁 Arborescence (extrait)

```
app/
├── api/
│   └── v1/
│       └── endpoints/      # Routes : ping, dig, etc.
├── core/                   # Middleware de sécurité
├── models/                 # Schémas de réponse
├── services/               # Logiciel métier
├── main.py                 # Point d’entrée
```

---

## 🧭 Roadmap

- [x] Authentification par API Key
- [x] Middleware de sécurité avec logs, rate-limit, validation
- [x] Tests unitaires pour `/ping`
- [x] Tests sécurité sur tous les endpoints
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
