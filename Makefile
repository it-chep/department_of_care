# Цвета
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

.PHONY: app
app:
	@printf "${GREEN}[+] INFO Starting application containers in detached mode...${NC}"
	@docker-compose up --build -d || (echo "Failed to start containers"; exit 1)
	@printf "${GREEN}[+] INFO Containers started successfully${NC}"
	@docker-compose ps


.PHONY: stop
stop:
	@printf "${GREEN} [+] INFO Stopping containers...${NC}"
	@docker-compose stop
	@printf "${GREEN} [+] INFO Containers stopped successfully${NC}"
	@docker-compose ps

.PHONY: empty_base
empty_base:
	@printf "${GREEN}[+] INFO Starting empty PostgreSQL container...${NC}"
	@docker run --name empty_postgres \
		-e POSTGRES_USER=readydog \
		-e POSTGRES_PASSWORD=JWaPsJdez19fLJkyPiHi9W \
		-e POSTGRES_DB=readydog \
		-p 5432:5432 \
		-d postgres:13-alpine
	@printf "${GREEN}[+] INFO PostgreSQL container started on port 5433 ${NC}"
	@printf "${GREEN}[+] INFO Connection string: postgresql://empty:empty@localhost:5433/empty ${NC}"



.PHONY: venv

VENV_NAME := .venv
PYTHON := python3
PIP := pip3
REQUIREMENTS := requirements.txt

venv:
	@if [ -d "$(VENV_NAME)" ]; then \
		printf "${GREEN}[+] INFO Virtual environment '$(VENV_NAME)' already exists. ${NC}"; \
		. $(VENV_NAME)/bin/activate; \
	else \
		printf "${GREEN}[+] INFO Creating virtual environment '$(VENV_NAME)'... ${NC}"; \
		$(PYTHON) -m venv $(VENV_NAME); \
		. $(VENV_NAME)/bin/activate && $(PIP) install --upgrade pip && $(PIP) install -r $(REQUIREMENTS); \
		printf "${GREEN}[+] INFO Virtual environment created. ${NC}"; \
	fi
	@printf "${GREEN}\n[+] INFO Current Python version:${NC}"
	@. $(VENV_NAME)/bin/activate && python --version

