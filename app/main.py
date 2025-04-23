from fastapi import FastAPI
from app.api.v1.endpoints import ping, dig, whois, nslookup, traceroute, dns_full,nmap

app = FastAPI(
    title="Network Tools API",
    description="API pour exécuter des outils réseau via HTTP",
    version="1.0.0"
)

# Inclusion des routes
app.include_router(ping.router, prefix="/v1", tags=["Ping"])
app.include_router(dig.router, prefix="/v1", tags=["DNS"])
app.include_router(nslookup.router, prefix="/v1", tags=["DNS"])
app.include_router(whois.router, prefix="/v1", tags=["Whois"])
app.include_router(traceroute.router, prefix="/v1", tags=["Network"])
app.include_router(dns_full.router, prefix="/v1", tags=["DNS"])
app.include_router(nmap.router, prefix="/v1", tags=["Scanner"])


# Message racine (optionnel)
@app.get("/")
def root():
    return {
        "message": "Bienvenue sur l'API Réseau ! Accédez à /docs pour l'interface Swagger.",
        "endpoints": ["/v1/ping", "/v1/dig", "/v1/nslookup", "/v1/whois","/v1/network","/v1/dns_full","/v1/nmap"]
    }
