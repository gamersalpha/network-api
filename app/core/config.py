# À utiliser si tu veux charger des settings via .env
from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Network Tools API"
    debug: bool = True

    class Config:
        env_file = ".env"

settings = Settings()
