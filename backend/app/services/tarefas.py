"""Regras de negócio do recurso ``tarefas``.

O serviço não acessa o banco diretamente: delega a persistência ao
``TarefaRepository`` e devolve schemas Pydantic, nunca modelos ORM.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tarefa import TarefaModel
from app.repositories.tarefa_repository import TarefaRepository
from app.schemas.tarefa import Tarefa, TarefaAtualizacaoParcial, TarefaEntrada


class TarefaNaoEncontradaError(Exception):
    """Levantado quando o id informado não corresponde a nenhuma tarefa."""

    def __init__(self, tarefa_id: int) -> None:
        super().__init__(f"Tarefa {tarefa_id} não encontrada.")
        self.tarefa_id = tarefa_id


class TarefaService:
    """CRUD de tarefas sobre um ``TarefaRepository``."""

    def __init__(self, repositorio: TarefaRepository) -> None:
        self.repositorio = repositorio

    def _buscar(self, tarefa_id: int) -> TarefaModel:
        tarefa = self.repositorio.obter(tarefa_id)
        if tarefa is None:
            raise TarefaNaoEncontradaError(tarefa_id)
        return tarefa

    def listar(self, concluida: bool | None = None, limite: int = 100) -> list[Tarefa]:
        """Lista as tarefas, opcionalmente filtrando por ``concluida``."""
        tarefas = self.repositorio.listar(concluida=concluida, limite=limite)
        return [Tarefa.model_validate(t) for t in tarefas]

    def obter(self, tarefa_id: int) -> Tarefa:
        """Retorna a tarefa ou levanta ``TarefaNaoEncontradaError``."""
        return Tarefa.model_validate(self._buscar(tarefa_id))

    def criar(self, dados: TarefaEntrada) -> Tarefa:
        """Cria uma tarefa."""
        return Tarefa.model_validate(self.repositorio.criar(dados.model_dump()))

    def substituir(self, tarefa_id: int, dados: TarefaEntrada) -> Tarefa:
        """Substitui todos os campos editáveis da tarefa (semântica do PUT)."""
        tarefa = self._buscar(tarefa_id)
        return Tarefa.model_validate(
            self.repositorio.atualizar(tarefa, dados.model_dump())
        )

    def atualizar(self, tarefa_id: int, dados: TarefaAtualizacaoParcial) -> Tarefa:
        """Atualiza apenas os campos enviados (semântica do PATCH)."""
        tarefa = self._buscar(tarefa_id)
        campos = dados.model_dump(exclude_unset=True)
        return Tarefa.model_validate(self.repositorio.atualizar(tarefa, campos))

    def remover(self, tarefa_id: int) -> None:
        """Remove a tarefa ou levanta ``TarefaNaoEncontradaError``."""
        self.repositorio.remover(self._buscar(tarefa_id))


def get_tarefa_service(
    session: Annotated[Session, Depends(get_db)],
) -> TarefaService:
    """Dependência do FastAPI: serviço ligado à sessão da requisição."""
    return TarefaService(TarefaRepository(session))
