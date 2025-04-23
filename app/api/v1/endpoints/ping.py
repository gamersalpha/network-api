from fastapi import APIRouter, Query
from app.services.ping_service import PingService
from app.models.response_model import CommandResponse

router = APIRouter()

@router.get("/ping", response_model=CommandResponse)
def ping_host(host: str = Query(..., description="Adresse IP ou nom de domaine à pinger")):
    service = PingService()
    return service.run(host)
