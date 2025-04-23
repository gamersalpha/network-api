from fastapi import APIRouter, Query
from app.services.dig_service import DigService
from app.models.response_model import CommandResponse

router = APIRouter()

@router.get("/dig", response_model=CommandResponse)
def dig_lookup(
    host: str = Query(..., description="Nom de domaine à interroger"),
    record_type: str = Query("A", description="Type d'enregistrement DNS (A, MX, TXT, NS, etc.)")
):
    service = DigService()
    return service.run(host, record_type)
