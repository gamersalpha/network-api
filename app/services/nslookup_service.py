import subprocess
from app.models.response_model import CommandResponse
import re

class NslookupService:
    def run(self, host: str) -> CommandResponse:
        try:
            result = subprocess.run(
                ["nslookup", host],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10
            )

            if result.returncode != 0:
                return CommandResponse(
                    success=False,
                    output="",
                    error=(result.stderr or "").strip()
                )

            # Analyse de la sortie brute
            output = result.stdout.strip()
            dns_server = self.extract_field(output, r"Server:\s*(.*)")
            domain_name = self.extract_field(output, r"Name:\s*(.*)")
            resolved_ip = self.extract_field(output, r"Address:\s*(\d+\.\d+\.\d+\.\d+)$")

            data = {
                "dns_server": dns_server,
                "domain": domain_name,
                "ip": resolved_ip
            }

            return CommandResponse(
                success=True,
                output=data,
                error=None
            )

        except Exception as e:
            return CommandResponse(
                success=False,
                output="",
                error=str(e)
            )

    def extract_field(self, text: str, pattern: str) -> str:
        match = re.search(pattern, text, re.MULTILINE)
        return match.group(1).strip() if match else None
