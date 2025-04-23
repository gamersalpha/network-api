import subprocess
import platform
import re
from app.models.response_model import CommandResponse

class TracerouteService:
    def run(self, host: str) -> CommandResponse:
        try:
            system = platform.system().lower()
            command = ["tracert", host] if system == "windows" else ["traceroute", host]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30
            )

            if result.returncode != 0:
                return CommandResponse(
                    success=False,
                    output="",
                    error=(result.stderr or "").strip()
                )

            hops = self.parse_traceroute(result.stdout, system)
            return CommandResponse(
                success=True,
                output=hops,
                error=None
            )

        except subprocess.TimeoutExpired:
            return CommandResponse(
                success=False,
                output="",
                error="La commande traceroute a pris trop de temps (timeout dépassé)."
            )
        except Exception as e:
            return CommandResponse(success=False, output="", error=str(e))

    def parse_traceroute(self, output: str, system: str):
        lines = output.strip().splitlines()
        hops = []

        for line in lines:
            if system == "windows":
                match = re.match(r"\s*(\d+)\s+([^\s]+)\s+(.*)", line)
                if match:
                    hop, ip, _ = match.groups()
                    hops.append({"hop": int(hop), "ip": ip})
            else:
                match = re.match(r"\s*(\d+)\s+([^\s]+)\s+([\d.]+)\s+ms\s+([\d.]+)\s+ms\s+([\d.]+)\s+ms", line)
                if match:
                    hop, ip, t1, t2, t3 = match.groups()
                    hops.append({
                        "hop": int(hop),
                        "ip": ip,
                        "latency_ms": [float(t1), float(t2), float(t3)]
                    })
                else:
                    match_star = re.match(r"\s*(\d+)\s+\*\s+\*\s+\*", line)
                    if match_star:
                        hop = int(match_star.group(1))
                        hops.append({
                            "hop": hop,
                            "ip": "*",
                            "latency_ms": ["*", "*", "*"]
                        })

        return hops
