# 🔧 OpenWebUI Tool – Ping

Ce module permet à OpenWebUI d'interroger une API réseau (Network-API) pour exécuter la commande `ping` sur n'importe quel hôte ou domaine, via une interface simple.

---

## 📦 Objectif

- Interroger l'API `/v1/ping` à distance  
- Obtenir la sortie textuelle du ping dans OpenWebUI  
- Compatible avec API sécurisée via clé (`X-API-Key`)

---

## 🧠 Exemple de code `network_tools.py`

```python
import requests

class Tools:
    def __init__(
        self,
        api_base_url="http://host.docker.internal:8088",  # ← adapte selon ton setup
        api_key="dev_key_123456"
    ):
        self.api_base_url = api_base_url.rstrip("/")
        self.api_key = api_key

    def ping(self, host: str) -> str:
        """
        Envoie un ping via l'API à une IP ou un domaine.
        host : IP ou domaine (ex: 8.8.8.8, openai.com)
        """
        try:
            r = requests.get(
                f"{self.api_base_url}/v1/ping",
                params={"host": host},
                headers={"X-API-Key": self.api_key},
                timeout=5,
            )
            return r.text
        except Exception as e:
            return f"Erreur : {e}"
```

---

## ⚙️ Paramètres

- `api_base_url` : URL de ton instance FastAPI (ex: `http://localhost:8088`)
- `api_key` : Clé API définie côté serveur
- `host` : Cible à tester (IP ou domaine)

---

## ✅ Exemple d'appel dans OpenWebUI

```python
tools = Tools()
print(tools.ping("8.8.8.8"))
```

---

## 🧪 Tester en dehors d’OpenWebUI

Créer un fichier `test_ping.py` :

```python
from network_tools import Tools

tools = Tools(api_base_url="http://localhost:8088", api_key="dev_key_123456")
print(tools.ping("1.1.1.1"))
```

---

## 🚀 Déploiement

1. Place le fichier `network_tools.py` dans le répertoire `openWebUiTools/`
2. Redémarre OpenWebUI ou recharge les outils
3. Lance une commande comme :  
   ```
   ping(host="1.1.1.1")
   ```

---

## 🛠️ Notes

- Assurez-vous que l’API Network est bien accessible depuis OpenWebUI
- Pour Docker : utilisez `host.docker.internal` ou le nom de service `network-api` si dans le même `docker-compose.yml`

---

## 📝 TODO — Intégration des autres services réseau

L'intégration complète est en cours. Voici les outils prévus dans l'ordre logique recommandé :

| Ordre | Service        | Description                                      |
|-------|----------------|--------------------------------------------------|
| 1     | **Whois**      | Requête WHOIS d’un nom de domaine                |
| 2     | **Dig**        | Résolution DNS par enregistrement                |
| 3     | **Nslookup**   | Requête DNS basique (adresse IP d’un domaine)    |
| 4     | **Traceroute** | Trace du chemin réseau vers une IP/domaine       |
| 5     | **Nmap**       | Scan de ports (standard, custom, full)           |
| 6     | **DNS Full**   | Regroupe tous les enregistrements DNS            |

Chaque outil sera intégré dans OpenWebUI via un fichier `.py` dédié, dans le répertoire `openWebUiTools/`, suivant le modèle du `ping`.

---

Tu peux contribuer ou suivre l’avancement via le dépôt GitHub :  
👉 `https://github.com/<ton_user>/network-api`

---
