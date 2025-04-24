# Makefile pour Network API

.PHONY: help run test build docker-up docker-down clean

# Affiche toutes les commandes disponibles
help:
	@echo "Commandes disponibles :"
	@echo "  make run           - Lancer le projet en local (uvicorn)"
	@echo "  make test          - Exécuter les tests Pytest"
	@echo "  make build         - Build Docker"
	@echo "  make docker-up     - Lancer le conteneur Docker"
	@echo "  make docker-down   - Stopper et supprimer les conteneurs"
	@echo "  make clean         - Supprimer les fichiers inutiles"

# Lancer localement avec uvicorn
run:
	uvicorn app.main:app --reload --port 8088

# Lancer les tests unitaires
test:
	pytest tests/

# Build Docker
build:
	docker compose build

# Up Docker
docker-up:
	docker compose up

# Down Docker
docker-down:
	docker compose down

# Nettoyage
clean:
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	rm -rf logs/*.log
