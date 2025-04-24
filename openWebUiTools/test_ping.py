import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from openWebUiTools.network_tools import Tools
# test_ping.py
# ─────────────────────────────────────────────
# Script pour tester la classe Tools (ping)
# Utilise l'API réseau via HTTP avec clé API
# ─────────────────────────────────────────────

# Initialisation de l'objet Tools avec les bons paramètres
tools = Tools(
    api_base_url="http://localhost:8088",  # ← adapte si tu changes de config
    api_key="dev_key_123456"
)

# Liste des hôtes à tester
hosts_to_test = [
    "8.8.8.8",
    "1.1.1.1",
    "openai.com"
]

print("🔧 Test de l'API de ping via Tools :\n")

for host in hosts_to_test:
    print(f"➡️  Ping {host} :")
    result = tools.ping(host)
    print(result)
    print("-" * 60)
