"""Modelos Pydantic dos recursos ``produtos`` e ``movimentacoes``.

São independentes dos modelos ORM (``app.models``): definem o contrato
da API, enquanto o ORM define a tabela.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ProdutoEntrada(BaseModel):
    """Dados para criar (POST) ou editar (PUT) um produto.

    Não inclui ``quantidade``: o saldo só muda por movimentações.
    """

    nome: str = Field(min_length=2, max_length=80)
    descricao: str | None = Field(default=None, max_length=300)
    preco: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    estoque_minimo: int = Field(default=0, ge=0)


class Produto(ProdutoEntrada):
    """Produto como é devolvido pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    quantidade: int
    criado_em: datetime

    @computed_field
    @property
    def abaixo_do_minimo(self) -> bool:
        """Verdadeiro quando o saldo está abaixo do estoque mínimo."""
        return self.quantidade < self.estoque_minimo


class MovimentacaoEntrada(BaseModel):
    """Dados para registrar uma entrada ou saída de estoque."""

    tipo: Literal["entrada", "saida"]
    quantidade: int = Field(gt=0)
    observacao: str | None = Field(default=None, max_length=200)


class Movimentacao(MovimentacaoEntrada):
    """Movimentação como é devolvida pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    produto_id: int
    criada_em: datetime


class Resumo(BaseModel):
    """Indicadores gerais do estoque."""

    total_produtos: int
    total_unidades: int
    valor_total: Decimal
    abaixo_do_minimo: int
