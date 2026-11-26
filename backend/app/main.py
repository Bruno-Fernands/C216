"""Ponto de entrada da API do Controle de Estoque.

Responsável apenas pela inicialização da aplicação: cria a instância
do FastAPI, configura o CORS e registra os routers de ``app.routers``.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers import produtos

app = FastAPI(
    title="Controle de Estoque API",
    description="Projeto Final de C216 - Sistemas Distribuídos (L1)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins_lista,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(produtos.router)


@app.get("/", tags=["status"])
def raiz() -> dict:
    """Verificação de saúde (usada pelo healthcheck do Compose)."""
    return {"message": "Controle de Estoque API", "status": "ok"}
