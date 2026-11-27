"""Modelos ORM das tabelas ``produtos`` e ``movimentacoes``."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProdutoModel(Base):
    """Linha da tabela ``produtos``.

    ``quantidade`` não é editada diretamente: só muda por movimentações.
    """

    __tablename__ = "produtos"
    __table_args__ = (
        CheckConstraint("quantidade >= 0", name="ck_produtos_quantidade"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)
    descricao: Mapped[str | None] = mapped_column(String(300))
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantidade: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    estoque_minimo: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Apagar o produto apaga o histórico dele (cascade no ORM e no banco).
    movimentacoes: Mapped[list["MovimentacaoModel"]] = relationship(
        back_populates="produto", cascade="all, delete-orphan", passive_deletes=True
    )


class MovimentacaoModel(Base):
    """Linha da tabela ``movimentacoes``: uma entrada ou saída de estoque."""

    __tablename__ = "movimentacoes"
    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_movimentacoes_quantidade"),
        CheckConstraint("tipo IN ('entrada', 'saida')", name="ck_movimentacoes_tipo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    produto_id: Mapped[int] = mapped_column(
        ForeignKey("produtos.id", ondelete="CASCADE"), index=True
    )
    tipo: Mapped[str] = mapped_column(String(10))
    quantidade: Mapped[int] = mapped_column(Integer)
    observacao: Mapped[str | None] = mapped_column(String(200))
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    produto: Mapped[ProdutoModel] = relationship(back_populates="movimentacoes")
