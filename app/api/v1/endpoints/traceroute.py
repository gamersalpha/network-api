from fastapi import APIRouter, Query
from app.services.traceroute_service import TracerouteService
from app.models.response_model import CommandResponse

router = APIRouter()

@router.get("/traceroute", response_model=CommandResponse)
def trace_route(
    host: str = Query(..., description="Hôte ou domaine à tracer")
):
    return TracerouteService().run(host)
