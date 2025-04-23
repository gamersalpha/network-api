import subprocess
import platform
import re
from app.models.response_model import CommandResponse

class PingService:
    def run(self, host: str) -> CommandResponse:
        try:
            system = platform.system().lower()
            param = "-n" if system == "windows" else "-c"
            encoding = "cp850" if system == "windows" else "utf-8"

            result = subprocess.run(
                ["ping", param, "4", host],
                capture_output=True,
                text=True,
                encoding=encoding,
                timeout=10
            )

            if result.returncode != 0:
                return CommandResponse(
                    success=False,
                    output="",
                    error=(result.stderr or "").strip()
                )

            parsed = self.parse_ping(result.stdout, system)
            return CommandResponse(success=True, output=parsed, error=None)

        except Exception as e:
            return CommandResponse(success=False, output="", error=str(e))

    def parse_ping(self, output: str, system: str) -> dict:
        parsed = {
            "transmitted": None,
            "received": None,
            "packet_loss_percent": None,
            "rtt": {}
        }

        if system == "windows":
            transmitted = received = lost = None
            match = re.search(r"Envoyés = (\d+), Reçus = (\d+), Perdus = (\d+)", output)
            if match:
                transmitted, received, lost = map(int, match.groups())
                parsed["transmitted"] = transmitted
                parsed["received"] = received
                parsed["packet_loss_percent"] = round((lost / transmitted) * 100, 2)

            rtt_match = re.search(r"Minimum = (\d+)ms, Maximum = (\d+)ms, Moyenne = (\d+)ms", output)
            if rtt_match:
                min_rtt, max_rtt, avg_rtt = map(int, rtt_match.groups())
                parsed["rtt"] = {
                    "min": min_rtt,
                    "avg": avg_rtt,
                    "max": max_rtt
                }

        else:  # Linux/Unix
            match_stats = re.search(
                r"(\d+) packets transmitted, (\d+) received,.*?(\d+)% packet loss",
                output
            )
            if match_stats:
                transmitted, received, loss = match_stats.groups()
                parsed["transmitted"] = int(transmitted)
                parsed["received"] = int(received)
                parsed["packet_loss_percent"] = float(loss)

            rtt_match = re.search(
                r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)",
                output
            )
            if rtt_match:
                min_rtt, avg_rtt, max_rtt, mdev = map(float, rtt_match.groups())
                parsed["rtt"] = {
                    "min": min_rtt,
                    "avg": avg_rtt,
                    "max": max_rtt,
                    "mdev": mdev
                }

        return parsed
