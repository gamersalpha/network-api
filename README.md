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

## ⚙️ Installation locale

```bash
git clone https://github.com/gamersalpha/network-api.git
cd network-api

# Création de l'environnement virtuel
python -m venv venv

# Activation (selon OS)
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# Installation des dépendances
pip install -r requirements.txt

# Lancement de l'API
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

## 🧪 Exemple de requête

```http
GET /v1/nmap?host=scanme.nmap.org&scan_mode=custom&ports=22,80&only_open=true
```

Réponse :

```json
{
  "host": "scanme.nmap.org",
  "ports": [
    { "port": 22, "state": "open", "service": "ssh" },
    { "port": 80, "state": "open", "service": "http" }
  ]
}
```

---

## 🧭 Roadmap

- [ ] Authentification par API Key
- [ ] Support complet IPv6
- [ ] Export des résultats (JSON brut, CSV, XML)
- [ ] Mode batch (ex. : ping ou nmap sur plusieurs hôtes)

---

## 📄 Licence

**MIT** — Libre d’utilisation, modification et contribution

---

## 👨‍💻 Auteur

- GitHub : [@gamersalpha](https://github.com/gamersalpha)
