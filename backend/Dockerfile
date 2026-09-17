# ============================================================================
# Dockerfile do backend C216
# Imagem base: Python 3.12 slim (compatível com o `requires-python = ^3.12`)
# ============================================================================

FROM python:3.12-slim

# Evita escrita de bytecode e mantém logs sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.4.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app

# Instala o Poetry dentro da imagem
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

# Copia apenas os arquivos de dependências primeiro
# (aproveita o cache de camadas do Docker quando eles não mudam)
COPY pyproject.toml poetry.lock ./

# Instala apenas as dependências de produção
RUN poetry install --no-root --only main --no-interaction

# Copia o código da aplicação
COPY app ./app

# Porta exposta pela API
EXPOSE 8000

# Comando padrão: sobe o servidor uvicorn
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]