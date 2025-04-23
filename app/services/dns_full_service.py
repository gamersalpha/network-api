import subprocess
import re
from app.models.response_model import CommandResponse

class DNSFullService:
    def run(self, host: str, dns_server: str = None) -> CommandResponse:
        try:
            record_types = ["A", "AAAA", "MX", "TXT", "NS", "SOA"]
            all_records = {}

            for record_type in record_types:
                try:
                    # Construction de la commande DIG avec serveur DNS personnalisé
                    command = ["dig"]
                    if dns_server:
                        command.append(f"@{dns_server}")
                    command += [host, record_type]

                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        timeout=10
                    )

                    parsed = self.parse_dig(result.stdout)

                    if parsed["answers"]:
                        all_records[record_type] = parsed["answers"]
                    else:
                        all_records[record_type] = []  # Réponse vide

                except Exception as e:
                    all_records[record_type] = f"Error: {str(e)}"

            return CommandResponse(success=True, output=all_records, error=None)

        except Exception as e:
            return CommandResponse(success=False, output="", error=str(e))

    def parse_dig(self, output: str) -> dict:
        answers = []
        inside_answer_section = False

        for line in output.splitlines():
            if line.startswith(";; ANSWER SECTION:"):
                inside_answer_section = True
                continue

            if inside_answer_section:
                if line.startswith(";;") or line.strip() == "":
                    break  # Fin de la section
                parts = line.split()
                if len(parts) >= 5:
                    name, ttl, _, typ, data = parts[:5]
                    answers.append({
                        "name": name,
                        "ttl": int(ttl),
                        "type": typ,
                        "data": data
                    })

        return {"answers": answers}
