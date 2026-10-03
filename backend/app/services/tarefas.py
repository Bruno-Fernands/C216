"""Regras de negócio do recurso ``tarefas``.

Os dados ficam em memória (dicionário), o que mantém o recurso simples
e sem dependência de banco de dados nos testes.
"""

from app.schemas.tarefa import Tarefa, TarefaAtualizacaoParcial, TarefaEntrada


class TarefaNaoEncontradaError(Exception):
    """Levantado quando o id informado não corresponde a nenhuma tarefa."""

    def __init__(self, tarefa_id: int) -> None:
        super().__init__(f"Tarefa {tarefa_id} não encontrada.")
        self.tarefa_id = tarefa_id


class TarefaService:
    """CRUD de tarefas armazenadas em memória."""

    def __init__(self) -> None:
        self._tarefas: dict[int, Tarefa] = {}
        self._proximo_id = 1

    def listar(self, concluida: bool | None = None, limite: int = 100) -> list[Tarefa]:
        """Lista as tarefas, opcionalmente filtrando por ``concluida``."""
        tarefas = list(self._tarefas.values())
        if concluida is not None:
            tarefas = [t for t in tarefas if t.concluida == concluida]
        return tarefas[:limite]

    def obter(self, tarefa_id: int) -> Tarefa:
        """Retorna a tarefa ou levanta ``TarefaNaoEncontradaError``."""
        try:
            return self._tarefas[tarefa_id]
        except KeyError as exc:
            raise TarefaNaoEncontradaError(tarefa_id) from exc

    def criar(self, dados: TarefaEntrada) -> Tarefa:
        """Cria uma tarefa com o próximo id disponível."""
        tarefa = Tarefa(id=self._proximo_id, **dados.model_dump())
        self._tarefas[tarefa.id] = tarefa
        self._proximo_id += 1
        return tarefa

    def substituir(self, tarefa_id: int, dados: TarefaEntrada) -> Tarefa:
        """Substitui todos os campos da tarefa (semântica do PUT)."""
        self.obter(tarefa_id)
        tarefa = Tarefa(id=tarefa_id, **dados.model_dump())
        self._tarefas[tarefa_id] = tarefa
        return tarefa

    def atualizar(self, tarefa_id: int, dados: TarefaAtualizacaoParcial) -> Tarefa:
        """Atualiza apenas os campos enviados (semântica do PATCH)."""
        atual = self.obter(tarefa_id)
        tarefa = atual.model_copy(update=dados.model_dump(exclude_unset=True))
        self._tarefas[tarefa_id] = tarefa
        return tarefa

    def remover(self, tarefa_id: int) -> None:
        """Remove a tarefa ou levanta ``TarefaNaoEncontradaError``."""
        self.obter(tarefa_id)
        del self._tarefas[tarefa_id]


_servico = TarefaService()


def get_tarefa_service() -> TarefaService:
    """Dependência do FastAPI: instância única usada pela aplicação."""
    return _servico
