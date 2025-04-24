
import pytest
import requests

BASE_URL = "http://localhost:8088"
DEV_KEY = "dev_key_123456"
ADMIN_KEY = "admin_key_654321"

# Endpoints avec paramètres de base et rôle requis
endpoints = [
    ("/v1/ping", {"host": "8.8.8.8"}, "dev"),
    ("/v1/nmap", {"host": "127.0.0.1", "scan_mode": "custom", "ports": "22"}, "admin"),
    ("/v1/whois", {"domain": "example.com"}, "dev"),
    ("/v1/dns-full", {"host": "google.com", "dns_server": "8.8.8.8"}, "dev"),
    ("/v1/dig", {"host": "openai.com", "record_type": "A"}, "dev"),
    ("/v1/nslookup", {"host": "example.com"}, "dev"),
    ("/v1/traceroute", {"host": "8.8.8.8"}, "dev")
]

# Payloads à bloquer
dangerous_inputs = [
    "8.8.8.8;rm -rf /",
    "example.com | echo hacked",
    "127.0.0.1 && shutdown now",
    "`ls -la`",
    "$(whoami)",
    "; cat /etc/passwd",
    "../etc/passwd",
    "8.8.8.8 > nul",
    "|| true"
]

@pytest.mark.parametrize("endpoint,params,role", endpoints)
@pytest.mark.parametrize("payload", dangerous_inputs)
def test_dangerous_inputs_are_blocked(endpoint, params, role, payload):
    test_params = params.copy()
    first_key = list(test_params.keys())[0]
    test_params[first_key] = payload

    api_key = ADMIN_KEY if role == "admin" else DEV_KEY

    print(f"🔍 Test de {endpoint} avec payload : {payload} (clé : {role})")

    response = requests.get(
        BASE_URL + endpoint,
        params=test_params,
        headers={"X-API-Key": api_key}
    )

    # Accepte 403 si le rôle n'est pas suffisant (cas rare ici car la bonne clé est utilisée)
    assert response.status_code in [400, 403], f"🚨 {endpoint} a accepté une payload dangereuse : {payload!r}"

    if response.status_code == 403:
        print(f"🔐 Refusé (403) → Accès admin requis ou rejet précoce")
    else:
        try:
            error_msg = response.json().get("error", "").lower()
        except Exception:
            error_msg = response.text.lower()

        assert any(term in error_msg for term in ["dangereux", "invalide", "paramètre"]), (
            f"⚠️ {endpoint} n'a pas renvoyé d'erreur explicite pour {payload!r}. Réponse : {response.text}"
        )
