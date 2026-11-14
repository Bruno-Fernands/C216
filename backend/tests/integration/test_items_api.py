"""Testes de integração do recurso ``/items/`` e do CORS."""

from fastapi.testclient import TestClient

ORIGEM = "http://localhost:5173"  # padrão de CORS_ORIGINS


def test_lista_vazia(client: TestClient) -> None:
    resposta = client.get("/items/")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_criar_e_listar(client: TestClient) -> None:
    resposta = client.post("/items/", json={"nome": "Caderno", "descricao": "Azul"})
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo.pop("criado_em")
    assert corpo == {"id": 1, "nome": "Caderno", "descricao": "Azul"}

    client.post("/items/", json={"nome": "Mochila", "descricao": "Preta"})
    assert [i["nome"] for i in client.get("/items/").json()] == ["Caderno", "Mochila"]


def test_nome_duplicado_responde_409(client: TestClient) -> None:
    client.post("/items/", json={"nome": "Caderno", "descricao": "A"})
    resposta = client.post("/items/", json={"nome": " Caderno ", "descricao": "B"})
    assert resposta.status_code == 409
    assert resposta.json() == {"detail": "Já existe um item com esse nome"}
    assert len(client.get("/items/").json()) == 1


def test_dados_invalidos_respondem_422(client: TestClient) -> None:
    resposta = client.post("/items/", json={"nome": "ab", "descricao": ""})
    assert resposta.status_code == 422


def test_preflight_cors_da_origem_permitida(client: TestClient) -> None:
    resposta = client.options(
        "/items/",
        headers={
            "Origin": ORIGEM,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resposta.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == ORIGEM


def test_cors_nao_libera_origem_desconhecida(client: TestClient) -> None:
    resposta = client.get("/items/", headers={"Origin": "http://malicioso.com"})
    assert "access-control-allow-origin" not in resposta.headers
