import os
from fastapi.testclient import TestClient
from app.main import app

# 🔑 Clé API depuis l'environnement (ou valeur de fallback)
VALID_API_KEY = os.getenv("API_KEY_DEV", "1234567890abcdef")
INVALID_API_KEY = "wrong-key"

client = TestClient(app)

def test_ping_success():
    response = client.get(
        "/v1/ping?host=8.8.8.8",
        headers={"X-API-Key": VALID_API_KEY}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "output" in json_data or "latency" in json_data

def test_ping_invalid_target():
    response = client.get(
        "/v1/ping?host=invalid.host",
        headers={"X-API-Key": VALID_API_KEY}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is False or "error" in json_data

def test_ping_missing_api_key():
    response = client.get("/v1/ping?host=8.8.8.8")
    assert response.status_code == 403
    assert response.json()["error"] == "Clé API invalide ou manquante"

def test_ping_invalid_api_key():
    response = client.get(
        "/v1/ping?host=8.8.8.8",
        headers={"X-API-Key": INVALID_API_KEY}
    )
    assert response.status_code == 403
    assert response.json()["error"] == "Clé API invalide ou manquante"
