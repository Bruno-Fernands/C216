"""Acesso aos dados da tabela ``tarefas``."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tarefa import TarefaModel


class TarefaRepository:
    """Operações de persistência de ``TarefaModel`` usando uma ``Session``."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar(
        self, concluida: bool | None = None, limite: int = 100
    ) -> list[TarefaModel]:
        """Lista as tarefas por ordem de id, com filtro e limite opcionais."""
        consulta = select(TarefaModel).order_by(TarefaModel.id).limit(limite)
        if concluida is not None:
            consulta = consulta.where(TarefaModel.concluida == concluida)
        return list(self.session.scalars(consulta))

    def obter(self, tarefa_id: int) -> TarefaModel | None:
        """Busca uma tarefa pela chave primária."""
        return self.session.get(TarefaModel, tarefa_id)

    def criar(self, campos: dict[str, Any]) -> TarefaModel:
        """Insere uma nova tarefa e devolve a linha persistida."""
        tarefa = TarefaModel(**campos)
        self.session.add(tarefa)
        self.session.commit()
        self.session.refresh(tarefa)
        return tarefa

    def atualizar(self, tarefa: TarefaModel, campos: dict[str, Any]) -> TarefaModel:
        """Altera os campos informados de uma tarefa existente."""
        for nome, valor in campos.items():
            setattr(tarefa, nome, valor)
        self.session.commit()
        self.session.refresh(tarefa)
        return tarefa

    def remover(self, tarefa: TarefaModel) -> None:
        """Apaga a tarefa do banco."""
        self.session.delete(tarefa)
        self.session.commit()
