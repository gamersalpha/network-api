FROM python:3.11-slim

WORKDIR /app

# Installer ping et autres outils réseau
RUN apt-get update && \
    apt-get install -y iputils-ping net-tools traceroute nmap dnsutils whois && \
    apt-get clean


# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
