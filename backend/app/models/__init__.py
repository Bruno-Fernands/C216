"""Modelos ORM (tabelas do banco).

Importar os modelos aqui garante que todos sejam registrados em
``Base.metadata`` (usado pelo Alembic no ``--autogenerate``).
"""

from app.models.produto import MovimentacaoModel, ProdutoModel

__all__ = ["MovimentacaoModel", "ProdutoModel"]
