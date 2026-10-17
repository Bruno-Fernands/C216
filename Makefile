# ============================================================================
# C216 - Makefile do projeto
# Comandos utilitários para o backend (Python/Poetry) e orquestração Docker
# Use `make help` para listar todos os comandos disponíveis.
# ============================================================================

# ----------------------------------------------------------------------------
# Variáveis
# ----------------------------------------------------------------------------
PYTHON       := python3
POETRY       := poetry
BACKEND      := backend
APP_MODULE   := app.main:app
HOST         := 0.0.0.0
PORT         := 8000
COMPOSE      := docker compose

# ----------------------------------------------------------------------------
# Alvos seguidos de '##' aparecem listados no `make help`
# ----------------------------------------------------------------------------
.PHONY: help install run build up down logs ps shell clean db test test-unit test-integration lint format migrate migration

help: ## Lista todos os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Instala as dependências do backend com Poetry
	cd $(BACKEND) && $(POETRY) install

run: ## Sobe o servidor FastAPI localmente (sem Docker)
	cd $(BACKEND) && $(POETRY) run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

build: ## Constrói as imagens Docker do projeto
	$(COMPOSE) build

up: ## Sobe os serviços (backend + banco) e espera ficarem saudáveis
	$(COMPOSE) up -d --wait

db: ## Sobe apenas o PostgreSQL (usado pelos testes de integração)
	$(COMPOSE) up -d --wait db

down: ## Derruba os serviços Docker
	$(COMPOSE) down

logs: ## Acompanha os logs dos serviços
	$(COMPOSE) logs -f --tail=100

ps: ## Lista o status dos serviços Docker
	$(COMPOSE) ps

shell: ## Abre um shell dentro do container do backend
	$(COMPOSE) exec backend sh

test: db ## Executa a suíte de testes completa (sobe o PostgreSQL)
	cd $(BACKEND) && $(POETRY) run pytest -v

test-unit: ## Executa apenas os testes unitários (não precisa de banco)
	cd $(BACKEND) && $(POETRY) run pytest tests/unit -v

test-integration: db ## Executa apenas os testes de integração (sobe o PostgreSQL)
	cd $(BACKEND) && $(POETRY) run pytest tests/integration -v

lint: ## Verifica estilo e formatação do código com o Ruff
	cd $(BACKEND) && $(POETRY) run ruff check . && $(POETRY) run ruff format --check .

format: ## Corrige o estilo e formata o código com o Ruff
	cd $(BACKEND) && $(POETRY) run ruff check --fix . && $(POETRY) run ruff format .

migrate: db ## Aplica as migrations pendentes no banco (Alembic)
	cd $(BACKEND) && $(POETRY) run alembic upgrade head

migration: db ## Gera uma migration a partir dos modelos: make migration msg="descricao"
	cd $(BACKEND) && $(POETRY) run alembic revision --autogenerate -m "$(msg)"

clean: ## Remove containers, volumes e artefatos locais
	$(COMPOSE) down -v
	rm -rf $(BACKEND)/.venv
	find . -type d -name '__pycache__' -exec rm -rf {} +