"""Acesso aos dados da tabela ``items``."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import ItemModel


class ItemRepository:
    """Operações de persistência de ``ItemModel`` usando uma ``Session``."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar(self) -> list[ItemModel]:
        """Lista os itens por ordem de criação (id)."""
        return list(self.session.scalars(select(ItemModel).order_by(ItemModel.id)))

    def criar(self, campos: dict[str, Any]) -> ItemModel:
        """Insere um item; levanta ``IntegrityError`` se o nome já existir."""
        item = ItemModel(**campos)
        self.session.add(item)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
        self.session.refresh(item)
        return item
