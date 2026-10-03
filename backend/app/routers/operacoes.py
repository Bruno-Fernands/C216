"""Endpoints base da API e das operações de ``app.services.operacoes``."""

from fastapi import APIRouter, HTTPException

from app.services.operacoes import dividir, saudacao, somar

router = APIRouter(tags=["operações"])


@router.get("/")
def raiz() -> dict:
    """Endpoint base da API."""
    return {"message": "C216 API", "status": "ok"}


@router.get("/saudacao/{nome}")
def obter_saudacao(nome: str) -> dict:
    """Retorna uma saudação personalizada."""
    return {"saudacao": saudacao(nome)}


@router.get("/somar")
def obter_soma(a: float, b: float) -> dict:
    """Soma dois números informados via query string."""
    return {"resultado": somar(a, b)}


@router.get("/dividir")
def obter_divisao(a: float, b: float) -> dict:
    """Divide dois números; responde 400 se o divisor for zero."""
    try:
        resultado = dividir(a, b)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"resultado": resultado}
