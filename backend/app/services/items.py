"""Regras de negócio do recurso ``items``."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.item_repository import ItemRepository
from app.schemas.item import Item, ItemEntrada


class ItemDuplicadoError(Exception):
    """Levantado quando já existe um item com o mesmo nome."""

    def __init__(self, nome: str) -> None:
        super().__init__("Já existe um item com esse nome")
        self.nome = nome


class ItemService:
    """Listagem e criação de itens sobre um ``ItemRepository``."""

    def __init__(self, repositorio: ItemRepository) -> None:
        self.repositorio = repositorio

    def listar(self) -> list[Item]:
        """Lista todos os itens."""
        return [Item.model_validate(i) for i in self.repositorio.listar()]

    def criar(self, dados: ItemEntrada) -> Item:
        """Cria um item ou levanta ``ItemDuplicadoError``.

        A unicidade é garantida pela constraint do banco (e não por um
        SELECT antes do INSERT), então duas requisições simultâneas com o
        mesmo nome não conseguem criar dois itens.
        """
        try:
            return Item.model_validate(self.repositorio.criar(dados.model_dump()))
        except IntegrityError as exc:
            raise ItemDuplicadoError(dados.nome) from exc


def get_item_service(session: Annotated[Session, Depends(get_db)]) -> ItemService:
    """Dependência do FastAPI: serviço ligado à sessão da requisição."""
    return ItemService(ItemRepository(session))
