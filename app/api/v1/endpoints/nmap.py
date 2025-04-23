from fastapi import APIRouter, Query
from app.services.nmap_service import NmapService
from app.models.response_model import CommandResponse

router = APIRouter()

@router.get("/nmap", response_model=CommandResponse)
def nmap_scan(
    host: str = Query(..., description="Cible à scanner (IP ou nom de domaine)"),
    scan_mode: str = Query("top100", description="Mode de scan : top100 | all | custom"),
    ports: str = Query(None, description="Ports à scanner si custom"),
    only_open: bool = Query(False, description="Afficher uniquement les ports ouverts")
):
    return NmapService().run(host, scan_mode, ports, only_open)