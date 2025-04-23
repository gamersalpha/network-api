from fastapi import APIRouter, Query
from app.services.dns_full_service import DNSFullService
from app.models.response_model import CommandResponse

router = APIRouter()

@router.get("/dns-full", response_model=CommandResponse)
def dns_full_lookup(
    host: str = Query(..., description="Nom de domaine à interroger"),
    dns_server: str = Query(None, description="Adresse IP du serveur DNS à utiliser (ex: 8.8.8.8)")
):
    return DNSFullService().run(host, dns_server)
