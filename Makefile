# ============================================================================
# C216 - Makefile do projeto
# Comandos utilitários para o backend (Python/Poetry)
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

# ----------------------------------------------------------------------------
# Alvos seguidos de '##' aparecem listados no `make help`
# ----------------------------------------------------------------------------
.PHONY: help install run

help: ## Lista todos os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Instala as dependências do backend com Poetry
	cd $(BACKEND) && $(POETRY) install

run: ## Sobe o servidor FastAPI com hot reload
	cd $(BACKEND) && $(POETRY) run uvicorn $(APP_MODULE) --host $(HOST) --port $(PORT) --reload