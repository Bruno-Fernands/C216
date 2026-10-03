"""Testes de integração da API (FastAPI) usando o TestClient."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Fixture que retorna um cliente de teste da aplicação."""
    return TestClient(app)


def test_raiz_ok(client: TestClient) -> None:
    """A rota raiz deve responder com status ok."""
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert resposta.json() == {"message": "C216 API", "status": "ok"}


def test_saudacao_endpoint(client: TestClient) -> None:
    """A rota /saudacao/{nome} deve retornar a saudação formatada."""
    resposta = client.get("/saudacao/matheus")
    assert resposta.status_code == 200
    assert resposta.json() == {"saudacao": "Olá, Matheus!"}


def test_somar_endpoint(client: TestClient) -> None:
    """A rota /somar deve somar os parâmetros da query string."""
    resposta = client.get("/somar", params={"a": 2, "b": 3})
    assert resposta.status_code == 200
    assert resposta.json() == {"resultado": 5}


def test_dividir_endpoint(client: TestClient) -> None:
    """A rota /dividir deve dividir os parâmetros da query string."""
    resposta = client.get("/dividir", params={"a": 10, "b": 2})
    assert resposta.status_code == 200
    assert resposta.json() == {"resultado": 5.0}


def test_dividir_por_zero_retorna_400(client: TestClient) -> None:
    """Divisão por zero na API deve retornar HTTP 400 com a mensagem de erro."""
    resposta = client.get("/dividir", params={"a": 1, "b": 0})
    assert resposta.status_code == 400
    assert "dividir por zero" in resposta.json()["detail"]