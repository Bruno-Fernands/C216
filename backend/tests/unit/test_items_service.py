"""Testes unitários de ``app.services.items`` e do schema ``ItemEntrada``.

O ``ItemRepository`` é trocado por um repositório falso em memória que
imita a constraint de nome único do banco (levanta ``IntegrityError``).
"""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings
from app.models.item import ItemModel
from app.schemas.item import ItemEntrada
from app.services.items import ItemDuplicadoError, ItemService


class RepositorioFalso:
    """Mesma interface do ``ItemRepository``, em memória."""

    def __init__(self) -> None:
        self.items: list[ItemModel] = []

    def listar(self) -> list[ItemModel]:
        return list(self.items)

    def criar(self, campos: dict[str, Any]) -> ItemModel:
        if any(i.nome == campos["nome"] for i in self.items):
            raise IntegrityError("INSERT", {}, Exception("unique"))
        item = ItemModel(id=len(self.items) + 1, criado_em=datetime.now(UTC), **campos)
        self.items.append(item)
        return item


@pytest.fixture
def servico() -> ItemService:
    return ItemService(RepositorioFalso())


def test_criar_e_listar(servico: ItemService) -> None:
    criado = servico.criar(ItemEntrada(nome="Caderno", descricao="Capa azul"))
    assert (criado.id, criado.nome, criado.descricao) == (1, "Caderno", "Capa azul")
    assert [i.nome for i in servico.listar()] == ["Caderno"]


def test_nome_duplicado_levanta_erro(servico: ItemService) -> None:
    servico.criar(ItemEntrada(nome="Caderno", descricao="A"))
    with pytest.raises(ItemDuplicadoError, match="Já existe um item com esse nome"):
        servico.criar(ItemEntrada(nome="Caderno", descricao="B"))
    assert len(servico.listar()) == 1


def test_schema_remove_espacos() -> None:
    dados = ItemEntrada(nome="  Caneta  ", descricao="  Azul ")
    assert (dados.nome, dados.descricao) == ("Caneta", "Azul")


@pytest.mark.parametrize(
    ("nome", "descricao"),
    [("ab", "ok"), ("a" * 51, "ok"), ("   ", "ok"), ("Item", ""), ("Item", "d" * 201)],
)
def test_schema_rejeita_dados_invalidos(nome: str, descricao: str) -> None:
    with pytest.raises(ValidationError):
        ItemEntrada(nome=nome, descricao=descricao)


def test_cors_origins_vira_lista() -> None:
    settings = Settings(cors_origins=" http://a.com , http://b.com ,")
    assert settings.cors_origins_lista == ["http://a.com", "http://b.com"]
