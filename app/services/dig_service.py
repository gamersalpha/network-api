import subprocess
import re
from app.models.response_model import CommandResponse

class DigService:
    def run(self, host: str, record_type: str) -> CommandResponse:
        try:
            result = subprocess.run(
                ["dig", host, record_type],
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

            parsed = self.parse_dig(result.stdout)
            return CommandResponse(
                success=True,
                output=parsed,
                error=None
            )

        except Exception as e:
            return CommandResponse(
                success=False,
                output="",
                error=str(e)
            )

    def parse_dig(self, output: str) -> dict:
        parsed = {
            "question": {},
            "answers": []
        }

        # Extraire la QUESTION
        question_match = re.search(r";([^ ]+)\.\s+IN\s+(\w+)", output)
        if question_match:
            parsed["question"]["name"] = question_match.group(1) + "."
            parsed["question"]["type"] = question_match.group(2)

        # Extraire la ANSWER SECTION
        answer_section = False
        for line in output.splitlines():
            if line.startswith(";; ANSWER SECTION:"):
                answer_section = True
                continue
            if answer_section:
                if line.startswith(";;"):
                    break  # fin de la section
                parts = line.split()
                if len(parts) >= 5:
                    name, ttl, _, typ, data = parts[:5]
                    parsed["answers"].append({
                        "name": name,
                        "ttl": int(ttl),
                        "type": typ,
                        "data": data
                    })

        return parsed
