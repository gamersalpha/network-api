import os
import re
import time
import logging
from typing import Dict, List, Optional, Set
from fastapi import Request, HTTPException, Depends, Security
from fastapi.responses import JSONResponse
from fastapi.security.api_key import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS, HTTP_400_BAD_REQUEST
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# 📁 S'assurer que le dossier de log existe
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.path.join(LOG_DIR, "api.log")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 🚨 Crée le logger
logger = logging.getLogger("api-security")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 👀 Regex de détection - Plus complète pour les injections
DANGEROUS_PATTERN = re.compile(r"[;&|$`><()\[\]{}]|\.\.\/|\/etc\/|\/var\/|\/bin\/")

# 🔐 Regex pour validation d'hôte
VALID_IP = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
VALID_DOMAIN = re.compile(r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")

# 🔑 API Keys depuis les variables d'environnement
API_KEYS = {
    os.getenv("API_KEY_DEV"): {
        "role": "developer", 
        "rate_limit": int(os.getenv("API_RATE_LIMIT_DEV", 30))
    },
    os.getenv("API_KEY_ADMIN"): {
        "role": "admin", 
        "rate_limit": int(os.getenv("API_RATE_LIMIT_ADMIN", 100))
    },
}

# Supprimer les clés vides (si une variable d'environnement n'existe pas)
API_KEYS = {k: v for k, v in API_KEYS.items() if k}

# Routes nécessitant des privilèges admin
ADMIN_ROUTES = {"/v1/nmap"}

# ⏱️ Stockage des requêtes pour le rate limiting
# Structure: {"ip_ou_api_key": [(timestamp1, endpoint1), (timestamp2, endpoint2), ...]}
request_history: Dict[str, List[tuple]] = {}

# 🛑 Liste noire d'IP
BLACKLISTED_IPS: Set[str] = set()

# API Key Header pour la validation via dépendances
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        endpoint = request.url.path
        query_params = dict(request.query_params)
        api_key = request.headers.get("X-API-Key")
        
        # 🚫 Vérification liste noire
        if client_ip in BLACKLISTED_IPS:
            logger.warning(f"🔒 IP bloquée: {client_ip} - Accès refusé à {endpoint}")
            return JSONResponse(
                status_code=HTTP_403_FORBIDDEN,
                content={"success": False, "error": "Adresse IP bloquée"}
            )

        # 🔑 Authentification API Key pour les endpoints protégés
        if endpoint.startswith("/v1/"):
            if not api_key or api_key not in API_KEYS:
                logger.warning(f"🔑 Authentification échouée: {client_ip} - {endpoint}")
                return JSONResponse(
                    status_code=HTTP_403_FORBIDDEN,
                    content={"success": False, "error": "Clé API invalide ou manquante"}
                )
            
            # 👑 Vérification des privilèges admin
            if endpoint in ADMIN_ROUTES and API_KEYS[api_key]["role"] != "admin":
                logger.warning(f"🔒 Privilèges insuffisants: {api_key} - {endpoint}")
                return JSONResponse(
                    status_code=HTTP_403_FORBIDDEN,
                    content={"success": False, "error": "Privilèges insuffisants pour cette opération"}
                )
                
            # ⏱️ Rate limiting
            user_id = api_key  # Utiliser la clé API comme identifiant
            current_time = time.time()
            rate_limit = API_KEYS[api_key]["rate_limit"]
            
            # Nettoyer l'historique (supprimer les requêtes de plus d'une minute)
            if user_id in request_history:
                request_history[user_id] = [
                    (ts, ep) for ts, ep in request_history[user_id] 
                    if current_time - ts < 60
                ]
                
                # Vérifier le nombre de requêtes
                if len(request_history[user_id]) >= rate_limit:
                    logger.warning(f"⏱️ Rate limit dépassé: {user_id} - {endpoint}")
                    return JSONResponse(
                        status_code=HTTP_429_TOO_MANY_REQUESTS,
                        content={"success": False, "error": "Limite de requêtes dépassée"}
                    )
            
            # Ajouter cette requête à l'historique
            if user_id not in request_history:
                request_history[user_id] = []
            request_history[user_id].append((current_time, endpoint))

        # 🛡️ Validation des paramètres
        for key, value in query_params.items():
            # Vérifier les caractères dangereux
            if DANGEROUS_PATTERN.search(value):
                log_msg = f"🚫 Requête bloquée - {request.method} {endpoint}?{request.query_params} [Paramètre '{key}' invalide]"
                logger.warning(log_msg)
                return JSONResponse(
                    status_code=HTTP_400_BAD_REQUEST,
                    content={"success": False, "error": f"Paramètre dangereux détecté dans '{key}'"}
                )
                
            # Validation spécifique pour les hôtes
            if key in ["host", "domain", "target", "hostname"] and value:
                if not (VALID_IP.match(value) or VALID_DOMAIN.match(value)):
                    log_msg = f"🚫 Hôte invalide - {request.method} {endpoint}?{request.query_params}"
                    logger.warning(log_msg)
                    return JSONResponse(
                        status_code=HTTP_400_BAD_REQUEST,
                        content={"success": False, "error": f"Format d'hôte invalide: '{value}'"}
                    )
                    
            # Validation spécifique pour ports (nmap)
            if key == "ports" and value:
                if not re.match(r"^(\d+,)*\d+$", value) or any(int(p) > 65535 for p in value.split(",") if p.isdigit()):
                    log_msg = f"🚫 Format de ports invalide - {request.method} {endpoint}?{request.query_params}"
                    logger.warning(log_msg)
                    return JSONResponse(
                        status_code=HTTP_400_BAD_REQUEST,
                        content={"success": False, "error": "Format de ports invalide"}
                    )

        # ✅ Traitement normal
        start_time = time.time()
        try:
            response = await call_next(request)
            duration = round((time.time() - start_time) * 1000)
            
            # Log selon le statut
            if response.status_code >= 400:
                logger.warning(f"⚠️ {request.method} {endpoint} → {response.status_code} ({duration}ms)")
            else:
                logger.info(f"✅ {request.method} {endpoint} → {response.status_code} ({duration}ms)")
                
            return response
            
        except Exception as e:
            duration = round((time.time() - start_time) * 1000)
            logger.error(f"🔥 Exception: {request.method} {endpoint} → {str(e)} ({duration}ms)")
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Erreur interne du serveur"}
            )

# ---- Fonctions utilitaires à utiliser dans les endpoints ----

async def validate_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Valide la clé API fournie dans l'en-tête de la requête.
    
    Args:
        api_key: Clé API fournie dans l'en-tête X-API-Key
        
    Returns:
        str: La clé API validée
        
    Raises:
        HTTPException: Si la clé API est invalide ou manquante
    """
    if not api_key or api_key not in API_KEYS:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Clé API invalide ou manquante"
        )
    return api_key

async def check_permissions(api_key: str = Depends(validate_api_key), required_role: str = "developer"):
    """
    Vérifie si l'utilisateur a les permissions nécessaires pour accéder à une ressource.
    
    Args:
        api_key: Clé API validée
        required_role: Rôle requis pour accéder à la ressource (developer, admin)
        
    Raises:
        HTTPException: Si l'utilisateur n'a pas les permissions nécessaires
    """
    if required_role == "admin" and API_KEYS[api_key]["role"] != "admin":
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Permissions insuffisantes. Rôle admin requis."
        )
    return True

def validate_host(host: str) -> bool:
    """
    Vérifie si un hôte est une adresse IP ou un nom de domaine valide.
    
    Args:
        host: Adresse IP ou nom de domaine à valider
        
    Returns:
        bool: True si l'hôte est valide, False sinon
    """
    return bool(VALID_IP.match(host) or VALID_DOMAIN.match(host))

def validate_ports(ports: str) -> bool:
    """
    Vérifie si une chaîne de ports est valide (format: "80" ou "80,443,8080").
    
    Args:
        ports: Chaîne de ports à valider
        
    Returns:
        bool: True si le format est valide, False sinon
    """
    if not re.match(r"^(\d+,)*\d+$", ports):
        return False
    
    # Vérifier que tous les ports sont dans la plage valide (1-65535)
    return all(1 <= int(p) <= 65535 for p in ports.split(",") if p.isdigit())