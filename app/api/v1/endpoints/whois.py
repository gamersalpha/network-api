from fastapi import APIRouter, Query
from app.services.whois_service import WhoisService
from app.models.response_model import CommandResponse

router = APIRouter()

@router.get("/whois", response_model=CommandResponse)
def whois_lookup(
    domain: str = Query(..., description="Nom de domaine à interroger (ex: google.com)")
):
    service = WhoisService()
    return service.run(domain)
