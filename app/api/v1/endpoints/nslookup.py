from fastapi import APIRouter, Query
from app.services.nslookup_service import NslookupService
from app.models.response_model import CommandResponse

router = APIRouter()

@router.get("/nslookup", response_model=CommandResponse)
def nslookup_lookup(host: str = Query(..., description="Nom de domaine ou IP")):
    return NslookupService().run(host)