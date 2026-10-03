"""Fixtures compartilhadas pelos testes de integração."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.tarefas import TarefaService, get_tarefa_service


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Cliente de teste da aplicação com um ``TarefaService`` vazio.

    A dependência é sobrescrita para que cada teste comece sem tarefas,
    evitando estado compartilhado entre os testes.
    """
    servico = TarefaService()
    app.dependency_overrides[get_tarefa_service] = lambda: servico
    yield TestClient(app)
    app.dependency_overrides.clear()
