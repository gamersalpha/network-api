import subprocess
import re
import logging
import platform
from typing import Dict, Any
from app.models.response_model import CommandResponse

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
    # Double validation côté service
    if not host or not isinstance(host, str):
        return CommandResponse(success=False, output=None, error="Hôte invalide")
    
    if not (1 <= count <= 10):
        return CommandResponse(success=False, output=None, error="Le nombre de paquets doit être entre 1 et 10")
    
    if not (1 <= timeout <= 5):
        return CommandResponse(success=False, output=None, error="Le timeout doit être entre 1 et 5 secondes")

    try:
        # Détection du système
        system = platform.system().lower()
        if system == "windows":
            command = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
        else:
            command = ["ping", "-c", str(count), "-W", str(timeout), host]

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout * count + 5,
            check=False
        )

        if process.returncode == 0:
            parsed = parse_ping_output(process.stdout, system)
            return CommandResponse(success=True, output=parsed, error=None)
        else:
            error_msg = "Hôte injoignable" if "100% packet loss" in process.stdout else process.stderr
            return CommandResponse(success=False, output=None, error=error_msg.strip())

    except subprocess.TimeoutExpired:
        logger.warning(f"Timeout lors du ping vers {host}")
        return CommandResponse(success=False, output=None, error="Timeout lors de l'exécution de la commande")

    except Exception as e:
        logger.error(f"Erreur pendant l'exécution du ping vers {host}: {str(e)}")
        return CommandResponse(success=False, output=None, error=f"Erreur: {str(e)}")

def parse_ping_output(output: str, system: str) -> Dict[str, Any]:
    """
    Parse la sortie de la commande ping selon le système d'exploitation.
    
    Args:
        output: Sortie brute de la commande ping
        system: Système d'exploitation (windows, linux, darwin)
    
    Returns:
        Dict: Résumé formaté des performances réseau
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

    host_match = re.search(r"Pinging ([^\s]+)|PING ([^\s]+)", output)
    if host_match:
        result["host"] = host_match.group(1) or host_match.group(2)

    if system == "windows":
        packets = re.search(r"Packets: Sent = (\d+), Received = (\d+), Lost = (\d+) \((\d+)% loss\)", output)
        if packets:
            result["packets_sent"] = int(packets.group(1))
            result["packets_received"] = int(packets.group(2))
            result["packet_loss_percent"] = int(packets.group(4))

        rtt = re.search(r"Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms", output)
        if rtt:
            result["rtt_min"] = float(rtt.group(1))
            result["rtt_max"] = float(rtt.group(2))
            result["rtt_avg"] = float(rtt.group(3))
    else:
        packets = re.search(r"(\d+) packets transmitted, (\d+) received.*?(\d+(?:\.\d+)?)% packet loss", output)
        if packets:
            result["packets_sent"] = int(packets.group(1))
            result["packets_received"] = int(packets.group(2))
            result["packet_loss_percent"] = float(packets.group(3))

        rtt = re.search(r"min/avg/max(?:/mdev)? = (\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)/(\d+(?:\.\d+)?)", output)
        if rtt:
            result["rtt_min"] = float(rtt.group(1))
            result["rtt_avg"] = float(rtt.group(2))
            result["rtt_max"] = float(rtt.group(3))

    result["status"] = get_ping_status(result["rtt_avg"], result["packet_loss_percent"])
    return result

def get_ping_status(avg_time: float, packet_loss: float) -> str:
    """
    Détermine la qualité de la connexion selon les résultats du ping.
    
    Returns:
        str: Niveau de qualité (excellent, good, fair, poor)
    """
    if packet_loss > 20:
        return "poor"
    elif packet_loss > 5:
        return "fair"
    elif avg_time <= 30:
        return "excellent"
    elif avg_time <= 100:
        return "good"
    return "fair"
