"""Modelo ORM da tabela ``tarefas``."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, false, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TarefaModel(Base):
    """Linha da tabela ``tarefas``."""

    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(100))
    descricao: Mapped[str | None] = mapped_column(String(500))
    concluida: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false()
    )
    criada_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
