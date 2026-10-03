"""Ponto de entrada da API FastAPI do projeto C216.

Responsável apenas pela inicialização da aplicação: cria a instância
do FastAPI e registra os routers definidos em ``app.routers``.
"""

from fastapi import FastAPI

from app.routers import operacoes, tarefas

app = FastAPI(
    title="C216 API",
    description="Backend da disciplina C216 - Sistemas Distribuídos (L1)",
    version="0.2.0",
)

app.include_router(operacoes.router)
app.include_router(tarefas.router)
