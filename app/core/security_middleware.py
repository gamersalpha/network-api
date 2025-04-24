import os
import re
import time
import logging
import ipaddress
from typing import Dict, List, Optional, Set
from fastapi import Request, HTTPException, Depends, Security
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS, HTTP_400_BAD_REQUEST
from dotenv import load_dotenv

# 🔄 Variables d’environnement
load_dotenv()

LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "api.log")

os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("api-security")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
logger.addHandler(file_handler)

# 🧪 Expressions régulières
DANGEROUS_PATTERN = re.compile(r"[;&|$`><()\[\]{}]|\.\.\/|\/etc\/|\/var\/|\/bin\/")
VALID_DOMAIN = re.compile(r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")

# 🔑 Clés API
API_KEYS = {
    os.getenv("API_KEY_DEV"): {"role": "developer", "rate_limit": int(os.getenv("API_RATE_LIMIT_DEV", 30))},
    os.getenv("API_KEY_ADMIN"): {"role": "admin", "rate_limit": int(os.getenv("API_RATE_LIMIT_ADMIN", 100))}
}
API_KEYS = {k: v for k, v in API_KEYS.items() if k}

assert API_KEYS, "❌ Aucune clé API définie dans les variables d'environnement"

ADMIN_ROUTES = {"/v1/nmap"}
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# ⏱️ Historique en mémoire (remplaçable par Redis)
request_history: Dict[str, List[tuple]] = {}
BLACKLISTED_IPS: Set[str] = set()

def is_valid_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        endpoint = request.url.path
        query_params = dict(request.query_params)
        api_key = request.headers.get("X-API-Key", "").strip()[:128]  # Strip & Limit
        #logger.info(f"🔐 [DEBUG] Clé reçue depuis header : {api_key}")
        #logger.info(f"🔐 [DEBUG] Clés autorisées : {list(API_KEYS.keys())}")
        if api_key not in API_KEYS:
            logger.warning(f"❌ Clé API invalide : '{api_key}'")



        if client_ip in BLACKLISTED_IPS:
            logger.warning(f"🔒 IP bloquée: {client_ip} - {endpoint}")
            return JSONResponse(status_code=HTTP_403_FORBIDDEN, content={"success": False, "error": "Adresse IP bloquée"})

        if endpoint.startswith("/v1/"):
            if not api_key or api_key not in API_KEYS:
                logger.warning(f"🔑 Auth échouée: {client_ip} - {endpoint}")
                return JSONResponse(status_code=HTTP_403_FORBIDDEN, content={"success": False, "error": "Clé API invalide ou manquante"})

            # Privilèges
            if endpoint in ADMIN_ROUTES and API_KEYS[api_key]["role"] != "admin":
                logger.warning(f"🔒 Privilèges insuffisants: {api_key} - {endpoint}")
                return JSONResponse(status_code=HTTP_403_FORBIDDEN, content={"success": False, "error": "Privilèges insuffisants"})

            # Rate limit
            user_id = api_key
            now = time.time()
            rate_limit = API_KEYS[api_key]["rate_limit"]

            if user_id not in request_history:
                request_history[user_id] = []
            request_history[user_id] = [(ts, ep) for ts, ep in request_history[user_id] if now - ts < 60]

            if len(request_history[user_id]) >= rate_limit:
                logger.warning(f"⏱️ Rate limit dépassé: {user_id} - {endpoint}")
                return JSONResponse(status_code=HTTP_429_TOO_MANY_REQUESTS, content={"success": False, "error": "Trop de requêtes"})

            request_history[user_id].append((now, endpoint))

        logger.info(f"🔍 [DEBUG] Query params reçus : {query_params}")
        # 🔍 Validation des paramètres
        for key, value in query_params.items():
            if DANGEROUS_PATTERN.search(value):
                logger.warning(f"🚫 Paramètre suspect ({key}) → {endpoint}?{request.query_params}")
                return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"success": False, "error": f"Paramètre invalide : '{key}'"})

            if key in ["host", "domain", "target", "hostname"] and value:
                if not (is_valid_ip(value) or VALID_DOMAIN.match(value)):
                    logger.warning(f"🚫 Hôte invalide: {value} - {endpoint}")
                    return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"success": False, "error": f"Hôte invalide: '{value}'"})

            if key == "ports" and value:
                if not re.match(r"^(\d+,)*\d+$", value) or any(int(p) > 65535 for p in value.split(",") if p.isdigit()):
                    logger.warning(f"🚫 Ports invalides: {value} - {endpoint}")
                    return JSONResponse(status_code=HTTP_400_BAD_REQUEST, content={"success": False, "error": "Format de ports invalide"})

        # ✅ Traitement normal
        try:
            start = time.time()
            response = await call_next(request)
            duration = round((time.time() - start) * 1000)

            log_msg = f"{request.method} {endpoint} → {response.status_code} ({duration}ms)"
            logger.warning(f"⚠️ {log_msg}") if response.status_code >= 400 else logger.info(f"✅ {log_msg}")
            return response

        except HTTPException as e:
            logger.warning(f"🚨 HTTPException: {e.detail} ({e.status_code})")
            return JSONResponse(status_code=e.status_code, content={"success": False, "error": e.detail})

        except Exception as e:
            logger.error(f"🔥 Erreur serveur: {str(e)}")
            return JSONResponse(status_code=500, content={"success": False, "error": "Erreur interne du serveur"})
        
async def validate_api_key(api_key: str = Security(api_key_header)) -> str:
        """
        Valide la clé API fournie dans l'en-tête.
        """
        if not api_key or api_key not in API_KEYS:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Clé API invalide ou manquante"
            )
        return api_key

async def check_permissions(api_key: str = Depends(validate_api_key), required_role: str = "developer"):
        """
        Vérifie les permissions associées à la clé API.
        """
        if required_role == "admin" and API_KEYS[api_key]["role"] != "admin":
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Permissions insuffisantes. Rôle admin requis."
            )
        return True
    

__all__ = ["SecurityMiddleware", "validate_api_key", "check_permissions"]    