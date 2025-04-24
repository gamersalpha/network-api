from fastapi import FastAPI
from app.api.v1 import endpoints  # Import centralisé depuis __init__.py
from app.core.security_middleware import SecurityMiddleware

app = FastAPI(
    title="Network Tools API",
    description="API pour exécuter des outils réseau via HTTP",
    version="1.0.0"
)

# 🛡️ Middleware de sécurité
app.add_middleware(SecurityMiddleware)

# 📡 Inclusion des routes versionnées
app.include_router(endpoints.ping.router, prefix="/v1", tags=["Ping"])
app.include_router(endpoints.dig.router, prefix="/v1", tags=["DNS"])
app.include_router(endpoints.nslookup.router, prefix="/v1", tags=["DNS"])
app.include_router(endpoints.dns_full.router, prefix="/v1", tags=["DNS"])
app.include_router(endpoints.whois.router, prefix="/v1", tags=["Whois"])
app.include_router(endpoints.traceroute.router, prefix="/v1", tags=["Network"])
app.include_router(endpoints.nmap.router, prefix="/v1", tags=["Scanner"])

# 🏠 Route de bienvenue
@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API Réseau ! Accédez à /docs pour Swagger UI.",
        "endpoints": [
            "/v1/ping", "/v1/dig", "/v1/nslookup", "/v1/whois",
            "/v1/traceroute", "/v1/dns_full", "/v1/nmap"
        ]
    }
