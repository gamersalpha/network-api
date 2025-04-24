
import pytest
import requests

BASE_URL = "http://localhost:8088"
DEV_KEY = "dev_key_123456"
ADMIN_KEY = "admin_key_654321"

@pytest.mark.parametrize("api_key", [DEV_KEY, ADMIN_KEY])
def test_ping_success(api_key):
    response = requests.get(
        f"{BASE_URL}/v1/ping",
        params={"host": "8.8.8.8"},
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert "output" in json_data

@pytest.mark.parametrize("api_key", [DEV_KEY, ADMIN_KEY])
def test_ping_invalid_target(api_key):
    response = requests.get(
        f"{BASE_URL}/v1/ping",
        params={"host": "invalid.host;rm -rf /"},
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 400
    json_data = response.json()
    assert json_data["success"] is False
    assert "error" in json_data

def test_ping_missing_api_key():
    response = requests.get(f"{BASE_URL}/v1/ping", params={"host": "8.8.8.8"})
    assert response.status_code == 403
    assert "error" in response.json()

def test_ping_invalid_api_key():
    response = requests.get(
        f"{BASE_URL}/v1/ping",
        params={"host": "8.8.8.8"},
        headers={"X-API-Key": "wrong_key_0000"}
    )
    assert response.status_code == 403
    assert "error" in response.json()
