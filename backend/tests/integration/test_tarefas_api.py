"""Testes de integração do recurso ``/tarefas`` usando o TestClient."""

import pytest
from fastapi.testclient import TestClient


def criar(client: TestClient, **campos) -> dict:
    """Cria uma tarefa via API e retorna o corpo da resposta."""
    resposta = client.post("/tarefas", json={"titulo": "Estudar FastAPI", **campos})
    assert resposta.status_code == 201
    return resposta.json()


# ----------------------------------------------------------------------------
# POST /tarefas
# ----------------------------------------------------------------------------
def test_criar_tarefa(client: TestClient) -> None:
    """POST deve criar a tarefa e responder 201 com o id gerado."""
    resposta = client.post(
        "/tarefas", json={"titulo": "Estudar FastAPI", "descricao": "Prática 4"}
    )
    assert resposta.status_code == 201
    assert resposta.json() == {
        "id": 1,
        "titulo": "Estudar FastAPI",
        "descricao": "Prática 4",
        "concluida": False,
    }


@pytest.mark.parametrize(
    "corpo",
    [
        {},
        {"titulo": ""},
        {"titulo": "x" * 101},
        {"titulo": "ok", "concluida": "talvez"},
    ],
)
def test_criar_tarefa_invalida_retorna_422(client: TestClient, corpo: dict) -> None:
    """POST com corpo inválido deve ser rejeitado pelo modelo Pydantic."""
    resposta = client.post("/tarefas", json=corpo)
    assert resposta.status_code == 422


# ----------------------------------------------------------------------------
# GET /tarefas
# ----------------------------------------------------------------------------
def test_listar_tarefas_vazio(client: TestClient) -> None:
    """GET sem tarefas cadastradas deve retornar uma lista vazia."""
    resposta = client.get("/tarefas")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_listar_tarefas(client: TestClient) -> None:
    """GET deve retornar todas as tarefas cadastradas."""
    criar(client, titulo="A")
    criar(client, titulo="B")
    resposta = client.get("/tarefas")
    assert resposta.status_code == 200
    assert [t["titulo"] for t in resposta.json()] == ["A", "B"]


@pytest.mark.parametrize("concluida,esperado", [(True, ["B"]), (False, ["A", "C"])])
def test_listar_tarefas_filtra_por_concluida(
    client: TestClient, concluida: bool, esperado: list[str]
) -> None:
    """Query parameter ``concluida`` deve filtrar a listagem."""
    criar(client, titulo="A")
    criar(client, titulo="B", concluida=True)
    criar(client, titulo="C")
    resposta = client.get("/tarefas", params={"concluida": concluida})
    assert resposta.status_code == 200
    assert [t["titulo"] for t in resposta.json()] == esperado


def test_listar_tarefas_com_limite(client: TestClient) -> None:
    """Query parameter ``limite`` deve restringir a quantidade de itens."""
    for titulo in ("A", "B", "C"):
        criar(client, titulo=titulo)
    resposta = client.get("/tarefas", params={"limite": 2})
    assert resposta.status_code == 200
    assert [t["titulo"] for t in resposta.json()] == ["A", "B"]


@pytest.mark.parametrize("limite", [0, 101])
def test_listar_tarefas_limite_invalido_retorna_422(
    client: TestClient, limite: int
) -> None:
    """``limite`` fora do intervalo 1..100 deve retornar HTTP 422."""
    resposta = client.get("/tarefas", params={"limite": limite})
    assert resposta.status_code == 422


# ----------------------------------------------------------------------------
# GET /tarefas/{tarefa_id}
# ----------------------------------------------------------------------------
def test_obter_tarefa(client: TestClient) -> None:
    """GET por id deve retornar a tarefa correspondente."""
    tarefa = criar(client)
    resposta = client.get(f"/tarefas/{tarefa['id']}")
    assert resposta.status_code == 200
    assert resposta.json() == tarefa


def test_obter_tarefa_inexistente_retorna_404(client: TestClient) -> None:
    """GET de um id inexistente deve retornar HTTP 404."""
    resposta = client.get("/tarefas/99")
    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Tarefa 99 não encontrada."}


@pytest.mark.parametrize("tarefa_id", ["0", "-1", "abc"])
def test_obter_tarefa_id_invalido_retorna_422(
    client: TestClient, tarefa_id: str
) -> None:
    """Path parameter que não é um inteiro >= 1 deve retornar HTTP 422."""
    resposta = client.get(f"/tarefas/{tarefa_id}")
    assert resposta.status_code == 422


# ----------------------------------------------------------------------------
# PUT /tarefas/{tarefa_id}
# ----------------------------------------------------------------------------
def test_substituir_tarefa(client: TestClient) -> None:
    """PUT deve substituir todos os campos, voltando os omitidos ao padrão."""
    tarefa = criar(client, descricao="antiga", concluida=True)
    resposta = client.put(f"/tarefas/{tarefa['id']}", json={"titulo": "Novo título"})
    assert resposta.status_code == 200
    assert resposta.json() == {
        "id": tarefa["id"],
        "titulo": "Novo título",
        "descricao": None,
        "concluida": False,
    }
    assert client.get(f"/tarefas/{tarefa['id']}").json() == resposta.json()


def test_substituir_tarefa_inexistente_retorna_404(client: TestClient) -> None:
    """PUT em um id inexistente deve retornar HTTP 404."""
    resposta = client.put("/tarefas/99", json={"titulo": "Novo título"})
    assert resposta.status_code == 404


def test_substituir_tarefa_sem_titulo_retorna_422(client: TestClient) -> None:
    """PUT exige o corpo completo: sem ``titulo`` deve retornar HTTP 422."""
    tarefa = criar(client)
    resposta = client.put(f"/tarefas/{tarefa['id']}", json={"concluida": True})
    assert resposta.status_code == 422


# ----------------------------------------------------------------------------
# PATCH /tarefas/{tarefa_id}
# ----------------------------------------------------------------------------
def test_atualizar_tarefa_parcialmente(client: TestClient) -> None:
    """PATCH deve alterar apenas os campos enviados."""
    tarefa = criar(client, descricao="Prática 4")
    resposta = client.patch(f"/tarefas/{tarefa['id']}", json={"concluida": True})
    assert resposta.status_code == 200
    assert resposta.json() == {**tarefa, "concluida": True}
    assert client.get(f"/tarefas/{tarefa['id']}").json() == resposta.json()


def test_atualizar_tarefa_inexistente_retorna_404(client: TestClient) -> None:
    """PATCH em um id inexistente deve retornar HTTP 404."""
    resposta = client.patch("/tarefas/99", json={"concluida": True})
    assert resposta.status_code == 404


def test_atualizar_tarefa_invalida_retorna_422(client: TestClient) -> None:
    """PATCH com valor inválido deve retornar HTTP 422."""
    tarefa = criar(client)
    resposta = client.patch(f"/tarefas/{tarefa['id']}", json={"titulo": ""})
    assert resposta.status_code == 422


# ----------------------------------------------------------------------------
# DELETE /tarefas/{tarefa_id}
# ----------------------------------------------------------------------------
def test_remover_tarefa(client: TestClient) -> None:
    """DELETE deve responder 204 sem corpo e a tarefa deixa de existir."""
    tarefa = criar(client)
    resposta = client.delete(f"/tarefas/{tarefa['id']}")
    assert resposta.status_code == 204
    assert resposta.content == b""
    assert client.get(f"/tarefas/{tarefa['id']}").status_code == 404


def test_remover_tarefa_inexistente_retorna_404(client: TestClient) -> None:
    """DELETE de um id inexistente deve retornar HTTP 404."""
    resposta = client.delete("/tarefas/99")
    assert resposta.status_code == 404
