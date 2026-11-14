"""Endpoints do recurso ``items`` (usado pelo frontend)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.item import Item, ItemEntrada
from app.services.items import ItemDuplicadoError, ItemService, get_item_service

router = APIRouter(prefix="/items", tags=["items"])

Servico = Annotated[ItemService, Depends(get_item_service)]


@router.get("/", response_model=list[Item])
def listar_items(servico: Servico) -> list[Item]:
    """Lista todos os itens."""
    return servico.listar()


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
def criar_item(dados: ItemEntrada, servico: Servico) -> Item:
    """Cria um item; responde 409 se o nome já existir."""
    try:
        return servico.criar(dados)
    except ItemDuplicadoError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
