"""Modelos Pydantic do recurso ``items``.

As regras de tamanho são as mesmas de ``frontend/src/validation.js``.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemEntrada(BaseModel):
    """Dados enviados pelo cliente para criar um item."""

    # Remove espaços nas pontas antes de validar, como o frontend faz.
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=3, max_length=50)
    descricao: str = Field(min_length=1, max_length=200)


class Item(ItemEntrada):
    """Item como é devolvido pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    criado_em: datetime
