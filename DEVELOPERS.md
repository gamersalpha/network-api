# 🛠️ Guide développeur – Network API

Bienvenue ! Ce projet expose des outils réseau (ping, nmap, dig, etc.) via une API HTTP basée sur FastAPI.
Cette doc t'explique comment fonctionne le projet et comment tu peux facilement l’étendre ou le modifier.

------------------------------------------------------------
📁 Structure du projet

network-api/
├── app/
│   ├── main.py                ← Point d'entrée FastAPI
│   ├── api/                   ← Routes API
│   │   └── v1/endpoints/      ← Endpoints REST (ping.py, dig.py, etc.)
│   ├── services/              ← Logique métier (commandes système)
│   ├── models/                ← Modèles de réponse (CommandResponse)
│   └── core/                  ← (config, sécurité, à venir)
├── requirements.txt
├── Dockerfile
└── docker-compose.yml

------------------------------------------------------------
⚙️ Lancer le projet en local

git clone https://github.com/gamersalpha/network-api.git
cd network-api
python -m venv venv
venv\Scripts\activate     (ou source venv/bin/activate sous Linux/Mac)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8088

➡ Swagger UI : http://localhost:8088/docs

------------------------------------------------------------
➕ Ajouter un nouvel outil (ex: curl, arp, etc.)

1. Créer un fichier dans `services/` :
   Exemple : services/curl_service.py

2. Créer un endpoint correspondant dans `api/v1/endpoints/` :
   Exemple : endpoints/curl.py

3. Inclure le endpoint dans app/main.py :
   from app.api.v1.endpoints import curl
   app.include_router(curl.router, prefix="/v1", tags=["Curl"])

4. La réponse doit utiliser `CommandResponse`

------------------------------------------------------------
📦 Format de réponse standard

Toutes les routes renvoient un objet :

{
  "success": true,
  "output": ... (données ou message),
  "error": null
}

Classe définie dans : `models/response_model.py`

------------------------------------------------------------
🐳 Lancer avec Docker

docker compose up --build

➡ Swagger : http://localhost:8088/docs

------------------------------------------------------------
📚 Exemple de requêtes API

GET /v1/ping?host=8.8.8.8  
GET /v1/nmap?host=scanme.nmap.org&scan_mode=all&only_open=true  
GET /v1/dns-full?host=google.com&dns_server=8.8.8.8  

------------------------------------------------------------
✅ Bonnes pratiques

✔ 1 outil = 1 service + 1 endpoint  
✔ Pas de logique dans les endpoints  
✔ Toujours parser les réponses (JSON lisible)  
✔ Documenter les paramètres via FastAPI (Query)  
✔ Garder le projet modulaire et lisible

------------------------------------------------------------
📥 Contribuer

- Fork le repo
- Crée ta branche : `feature/ma-fonction`
- Push sur GitHub
- Ouvre une Pull Request 🚀

------------------------------------------------------------
🧠 Améliorations possibles

- Authentification avec API key
- Export CSV ou JSON
- Mode batch (multi-host)
- Scan UDP, scan IPv6
- Interface Web pour tester visuellement

------------------------------------------------------------
👨‍💻 Auteur

GitHub : https://github.com/gamersalpha  
Projet : https://github.com/gamersalpha/network-api
