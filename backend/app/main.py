"""API FastAPI do projeto C216.

Exposição HTTP das funções de negócio definidas em ``app.services``.
"""

from fastapi import FastAPI, HTTPException

from app.services import dividir, saudacao, somar

app = FastAPI(
    title="C216 API",
    description="Backend da disciplina C216 - Sistemas Distribuídos (L1)",
    version="0.1.0",
)


@app.get("/")
def raiz() -> dict:
    """Endpoint base da API."""
    return {"message": "C216 API", "status": "ok"}


@app.get("/saudacao/{nome}")
def obter_saudacao(nome: str) -> dict:
    """Retorna uma saudação personalizada."""
    return {"saudacao": saudacao(nome)}


@app.get("/somar")
def obter_soma(a: float, b: float) -> dict:
    """Soma dois números informados via query string."""
    return {"resultado": somar(a, b)}


@app.get("/dividir")
def obter_divisao(a: float, b: float) -> dict:
    """Divide dois números; responde 400 se o divisor for zero."""
    try:
        resultado = dividir(a, b)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"resultado": resultado}