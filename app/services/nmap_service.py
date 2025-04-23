import subprocess
from app.models.response_model import CommandResponse

class NmapService:
    def run(self, host: str, scan_mode: str = "top100", ports: str = None, only_open: bool = False) -> CommandResponse:
        try:
            command = ["nmap", "-sV", "-Pn"]

            # Mode de scan
            if scan_mode == "all":
                command += ["-p-"]
                timeout = 300
            elif scan_mode == "custom" and ports:
                command += ["-p", ports]
                timeout = 60
            else:
                command += ["--top-ports", "100"]
                timeout = 30

            command.append(host)

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout
            )

            if result.returncode != 0:
                return CommandResponse(
                    success=False,
                    output="",
                    error=(result.stderr or "").strip()
                )

            parsed = self.parse_nmap(result.stdout, host, only_open)
            return CommandResponse(success=True, output=parsed, error=None)

        except Exception as e:
            return CommandResponse(success=False, output="", error=str(e))

    def parse_nmap(self, output: str, host: str, only_open: bool) -> dict:
        ports = []
        capture = False

        for line in output.splitlines():
            if line.startswith("PORT"):
                capture = True
                continue

            if capture:
                if not line.strip() or line.startswith("Nmap done"):
                    break
                parts = line.split()
                if len(parts) >= 3 and "/" in parts[0]:
                    try:
                        port_proto = parts[0]
                        port = int(port_proto.split("/")[0])
                        state = parts[1]
                        service = parts[2]

                        if only_open and state.lower() != "open":
                            continue  # On ne garde que les ports ouverts si demandé

                        ports.append({
                            "port": port,
                            "state": state,
                            "service": service
                        })
                    except ValueError:
                        continue  # Ignore ligne non conforme

        return {
            "host": host,
            "ports": ports
        }
