import re

# Regex autorisant les noms de domaine, IP, FQDN
ALLOWED_HOST_REGEX = re.compile(r"^[a-zA-Z0-9.\-]+$")

# Caractères dangereux à éviter dans les inputs shell
BLACKLISTED_CHARS = r"[;&|$`><()\[\]{}]"

def is_safe_host(value: str) -> bool:
    """
    Vérifie si une entrée 'host' est valide (pas de caractères dangereux, format correct)
    """
    return bool(ALLOWED_HOST_REGEX.match(value))

def sanitize_input(value: str) -> str:
    """
    Supprime les caractères dangereux d'une chaîne
    """
    return re.sub(BLACKLISTED_CHARS, '', value)

def is_valid_port_range(value: str) -> bool:
    """
    Vérifie si la chaîne correspond à un port simple, une liste, ou une plage valide
    Exemples valides : '22', '80,443', '1000-2000'
    """
    return bool(re.match(r"^(\d+(-\d+)?)(,\d+(-\d+)?)*$", value))
