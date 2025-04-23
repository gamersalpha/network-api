import subprocess
from app.models.response_model import CommandResponse

class WhoisService:
    def run(self, domain: str) -> CommandResponse:
        try:
            result = subprocess.run(
                ["whois", domain],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10
            )
            return CommandResponse(
                success=result.returncode == 0,
                output=(result.stdout or "").strip(),
                error=(result.stderr or "").strip() if result.returncode != 0 else None
            )
        except Exception as e:
            return CommandResponse(
                success=False,
                output="",
                error=str(e)
            )
