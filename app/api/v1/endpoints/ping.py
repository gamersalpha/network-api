from fastapi import APIRouter, Query, Depends, HTTPException
from app.models.response_model import CommandResponse
from app.services.ping_service import execute_ping
from typing import Optional
from app.core.security_middleware import validate_api_key, check_permissions

router = APIRouter()

@router.get("/ping", response_model=CommandResponse, summary="Vérifier la connectivité d'un hôte")
async def ping(
    host: str = Query(..., description="Nom d'hôte ou adresse IP à pinger"),
    count: Optional[int] = Query(4, description="Nombre de paquets à envoyer", ge=1, le=10),
    timeout: Optional[int] = Query(2, description="Délai d'attente en secondes", ge=1, le=5),
    api_key: str = Depends(validate_api_key)
):
    """
    Vérifie la connectivité réseau avec un hôte distant en utilisant la commande PING.
    
    - Renvoie les temps de réponse et statistiques de perte de paquets
    - Utile pour vérifier si un serveur est en ligne et répondant
    """
    try:
        # L'authentification est déjà vérifiée par le middleware et la dépendance validate_api_key
        result = await execute_ping(host, count, timeout)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'exécution du ping: {str(e)}")