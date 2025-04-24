import pytest
import requests

BASE_URL = "http://localhost:8088"

# 🧪 Liste des endpoints + leurs paramètres valides de base
endpoints = [
    ("/v1/ping", {"host": "8.8.8.8"}),
    ("/v1/nmap", {"host": "127.0.0.1", "scan_mode": "custom", "ports": "22"}),
    ("/v1/whois", {"domain": "example.com"}),
    ("/v1/dns-full", {"host": "google.com", "dns_server": "8.8.8.8"}),
    ("/v1/dig", {"host": "openai.com", "record_type": "A"}),
    ("/v1/nslookup", {"host": "example.com"}),
    ("/v1/traceroute", {"host": "8.8.8.8"})
]

# 🎯 Payloads à rejeter
dangerous_inputs = [
    "8.8.8.8;rm -rf /",
    "example.com | echo hacked",
    "127.0.0.1 && shutdown now",
    "`ls -la`",
    "$(whoami)",
    "; cat /etc/passwd"
]

@pytest.mark.parametrize("endpoint,params", endpoints)
@pytest.mark.parametrize("payload", dangerous_inputs)
def test_dangerous_inputs_are_blocked(endpoint, params, payload):
    test_params = params.copy()
    first_key = list(params.keys())[0]
    test_params[first_key] = payload

    res = requests.get(BASE_URL + endpoint, params=test_params)

    assert res.status_code == 400, f"{endpoint} ACCEPTED payload {payload!r}"
    assert "dangereux" in res.text or "invalide" in res.text.lower(), f"{endpoint} did not return expected error for {payload!r}"
