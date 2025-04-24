import requests


class Tools:
    def __init__(
        self, api_base_url="http://host.docker.internal:8088", api_key="dev_key_123456"
    ):
        self.api_base_url = api_base_url.rstrip("/")
        self.api_key = api_key

    def ping(self, host: str) -> str:
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
