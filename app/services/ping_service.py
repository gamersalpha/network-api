import subprocess
import re
import logging
import platform
from app.models.response_model import CommandResponse
from typing import Dict, Any, List

logger = logging.getLogger("ping-service")

async def execute_ping(host: str, count: int = 4, timeout: int = 2) -> CommandResponse:
    """
    Exécute la commande ping vers un hôte spécifié de façon sécurisée.
    
    Args:
        host: Nom d'hôte ou adresse IP à pinger
        count: Nombre de paquets à envoyer
        timeout: Délai d'attente en secondes
    
    Returns:
        CommandResponse: Résultat formaté de la commande ping
    """
    # Sécurité: valider les entrées spécifiquement pour ping 
    # (bien que déjà validées par le middleware, double vérification ici)
    if not host or not isinstance(host, str):
        return CommandResponse(success=False, error="Hôte invalide")
    
    if not (1 <= count <= 10):
        return CommandResponse(success=False, error="Le nombre de paquets doit être entre 1 et 10")
    
    if not (1 <= timeout <= 5):
        return CommandResponse(success=False, error="Le timeout doit être entre 1 et 5 secondes")
    
    try:
        # Adapter la commande selon le système d'exploitation
        if platform.system().lower() == "windows":
            command = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
        else:  # Linux, MacOS
            command = ["ping", "-c", str(count), "-W", str(timeout), host]
        
        # Exécuter la commande de façon sécurisée
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout * count + 5,  # Timeout légèrement plus long que la durée attendue
            check=False  # Ne pas lever d'exception en cas d'erreur
        )
        
        # Analyser la sortie
        if process.returncode == 0:
            # Traiter la sortie pour une réponse formatée
            ping_data = parse_ping_output(process.stdout, platform.system())
            return CommandResponse(
                success=True,
                output=ping_data
            )
        else:
            # Hôte injoignable ou problème réseau
            error_msg = "Hôte injoignable" if "100% packet loss" in process.stdout else process.stderr
            return CommandResponse(
                success=False,
                error=error_msg
            )
            
    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout lors du ping vers {host}")
        return CommandResponse(success=False, error="Timeout lors de l'exécution de la commande")
    except Exception as e:
        logger.error(f"Erreur pendant l'exécution du ping vers {host}: {str(e)}")
        return CommandResponse(success=False, error=f"Erreur: {str(e)}")

def parse_ping_output(output: str, system: str) -> Dict[str, Any]:
    """
    Parse la sortie de la commande ping selon le système d'exploitation.
    
    Args:
        output: Sortie brute de la commande ping
        system: Système d'exploitation (Windows, Linux, Darwin)
        
    Returns:
        Dict: Informations formatées (paquets envoyés, perdus, temps min/max/avg)
    """
    result = {
        "host": "",
        "packets_sent": 0,
        "packets_received": 0,
        "packet_loss_percent": 0,
        "rtt_min": 0,
        "rtt_avg": 0,
        "rtt_max": 0,
        "raw_output": output.strip()
    }
    
    # Extraire l'hôte cible
    host_match = re.search(r"Pinging ([^\s]+)|PING ([^\s]+)", output)
    if host_match:
        result["host"] = host_match.group(1) if host_match.group(1) else host_match.group(2)
    
    # Extraire les statistiques selon le système
    if system.lower() == "windows":
        # Statistiques Windows
        packets_stats = re.search(r"Packets: Sent = (\d+), Received = (\d+), Lost = (\d+) \((\d+)% loss\)", output)
        if packets_stats:
            result["packets_sent"] = int(packets_stats.group(1))
            result["packets_received"] = int(packets_stats.group(2))
            result["packet_loss_percent"] = int(packets_stats.group(4))
        
        # Temps de réponse Windows
        rtt_stats = re.search(r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms", output)
        if rtt_stats:
            result["rtt_min"] = float(rtt_stats.group(1))
            result["rtt_max"] = float(rtt_stats.group(2))
            result["rtt_avg"] = float(rtt_stats.group(3))
    else:
        # Statistiques Linux/MacOS
        packets_stats = re.search(r"(\d+) packets transmitted, (\d+) received.+?(\d+(?:\.\d+)?)% packet loss", output)
        if packets_stats:
            result["packets_sent"] = int(packets_stats.group(1))
            result["packets_received"] = int(packets_stats.group(2))
            result["packet_loss_percent"] = float(packets_stats.group(3))
        
        # Temps de réponse Linux/MacOS
        rtt_stats = re.search(r"min/avg/max(?:/mdev)? = (\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)", output)
        if rtt_stats:
            result["rtt_min"] = float(rtt_stats.group(1))
            result["rtt_avg"] = float(rtt_stats.group(2))
            result["rtt_max"] = float(rtt_stats.group(3))
    
    # Ajouter des indications de performance
    result["status"] = get_ping_status(result["rtt_avg"], result["packet_loss_percent"])
    
    return result

def get_ping_status(avg_time: float, packet_loss: float) -> str:
    """
    Détermine la qualité de la connexion selon les métriques de ping.
    
    Args:
        avg_time: Temps de réponse moyen (ms)
        packet_loss: Pourcentage de paquets perdus
        
    Returns:
        str: Statut de la connexion (excellent, good, fair, poor)
    """
    if packet_loss > 20:
        return "poor"
    elif packet_loss > 5:
        return "fair"
    elif avg_time <= 30:
        return "excellent"
    elif avg_time <= 100:
        return "good"
    else:
        return "fair"