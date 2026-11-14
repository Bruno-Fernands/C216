"""Testes unitários das regras de negócio em ``app.services.tarefas``.

O ``TarefaRepository`` é substituído por um repositório falso em memória,
então estes testes não precisam de banco de dados.
"""

from datetime import UTC, datetime
from typing import Any

import pytest

from app.models.tarefa import TarefaModel
from app.schemas.tarefa import Tarefa, TarefaAtualizacaoParcial, TarefaEntrada
from app.services.tarefas import TarefaNaoEncontradaError, TarefaService


class RepositorioFalso:
    """Implementa a mesma interface do ``TarefaRepository`` em memória."""

    def __init__(self) -> None:
        self.tarefas: dict[int, TarefaModel] = {}
        self.proximo_id = 1

    def listar(
        self, concluida: bool | None = None, limite: int = 100
    ) -> list[TarefaModel]:
        tarefas = list(self.tarefas.values())
        if concluida is not None:
            tarefas = [t for t in tarefas if t.concluida == concluida]
        return tarefas[:limite]

    def obter(self, tarefa_id: int) -> TarefaModel | None:
        return self.tarefas.get(tarefa_id)

    def criar(self, campos: dict[str, Any]) -> TarefaModel:
        tarefa = TarefaModel(id=self.proximo_id, criada_em=datetime.now(UTC), **campos)
        self.tarefas[tarefa.id] = tarefa
        self.proximo_id += 1
        return tarefa

    def atualizar(self, tarefa: TarefaModel, campos: dict[str, Any]) -> TarefaModel:
        for nome, valor in campos.items():
            setattr(tarefa, nome, valor)
        return tarefa

    def remover(self, tarefa: TarefaModel) -> None:
        del self.tarefas[tarefa.id]


@pytest.fixture
def repositorio() -> RepositorioFalso:
    """Repositório falso vazio para cada teste."""
    return RepositorioFalso()


@pytest.fixture
def servico(repositorio: RepositorioFalso) -> TarefaService:
    """Serviço usando o repositório falso."""
    return TarefaService(repositorio)


def test_criar_devolve_schema_e_nao_modelo_orm(servico: TarefaService) -> None:
    """O serviço converte o modelo ORM no schema Pydantic ``Tarefa``."""
    tarefa = servico.criar(TarefaEntrada(titulo="A"))
    assert isinstance(tarefa, Tarefa)
    assert (tarefa.id, tarefa.titulo, tarefa.concluida) == (1, "A", False)


def test_criar_repassa_campos_ao_repositorio(
    servico: TarefaService, repositorio: RepositorioFalso
) -> None:
    """Os dados validados chegam ao repositório."""
    servico.criar(TarefaEntrada(titulo="A", descricao="x", concluida=True))
    salvo = repositorio.tarefas[1]
    assert (salvo.titulo, salvo.descricao, salvo.concluida) == ("A", "x", True)


def test_obter(servico: TarefaService) -> None:
    """``obter`` devolve a tarefa criada."""
    tarefa = servico.criar(TarefaEntrada(titulo="A"))
    assert servico.obter(tarefa.id) == tarefa


@pytest.mark.parametrize("operacao", ["obter", "remover"])
def test_id_inexistente_levanta_erro(servico: TarefaService, operacao: str) -> None:
    """Operações em um id inexistente levantam ``TarefaNaoEncontradaError``."""
    with pytest.raises(TarefaNaoEncontradaError, match="Tarefa 7 não encontrada"):
        getattr(servico, operacao)(7)


def test_substituir_e_atualizar_id_inexistente(servico: TarefaService) -> None:
    """``substituir`` e ``atualizar`` também validam a existência do id."""
    with pytest.raises(TarefaNaoEncontradaError):
        servico.substituir(7, TarefaEntrada(titulo="A"))
    with pytest.raises(TarefaNaoEncontradaError):
        servico.atualizar(7, TarefaAtualizacaoParcial(concluida=True))


@pytest.mark.parametrize(
    "concluida,limite,esperado",
    [
        (None, 100, ["A", "B", "C"]),
        (True, 100, ["B"]),
        (False, 100, ["A", "C"]),
        (None, 2, ["A", "B"]),
    ],
)
def test_listar_repassa_filtro_e_limite(
    servico: TarefaService, concluida: bool | None, limite: int, esperado: list[str]
) -> None:
    """``listar`` repassa filtro e limite e devolve schemas."""
    servico.criar(TarefaEntrada(titulo="A"))
    servico.criar(TarefaEntrada(titulo="B", concluida=True))
    servico.criar(TarefaEntrada(titulo="C"))
    tarefas = servico.listar(concluida=concluida, limite=limite)
    assert [t.titulo for t in tarefas] == esperado
    assert all(isinstance(t, Tarefa) for t in tarefas)


def test_substituir_redefine_campos_omitidos(servico: TarefaService) -> None:
    """``substituir`` troca todos os campos editáveis, mantendo o id."""
    tarefa = servico.criar(TarefaEntrada(titulo="A", descricao="x", concluida=True))
    nova = servico.substituir(tarefa.id, TarefaEntrada(titulo="B"))
    assert (nova.id, nova.titulo, nova.descricao, nova.concluida) == (
        tarefa.id,
        "B",
        None,
        False,
    )
    assert nova.criada_em == tarefa.criada_em


def test_atualizar_altera_apenas_campos_enviados(servico: TarefaService) -> None:
    """``atualizar`` preserva os campos que não foram enviados."""
    tarefa = servico.criar(TarefaEntrada(titulo="A", descricao="x"))
    nova = servico.atualizar(tarefa.id, TarefaAtualizacaoParcial(concluida=True))
    assert nova == tarefa.model_copy(update={"concluida": True})


def test_atualizar_permite_limpar_descricao(servico: TarefaService) -> None:
    """Enviar ``descricao=None`` explicitamente limpa o campo."""
    tarefa = servico.criar(TarefaEntrada(titulo="A", descricao="x"))
    nova = servico.atualizar(tarefa.id, TarefaAtualizacaoParcial(descricao=None))
    assert nova.descricao is None


def test_remover(servico: TarefaService) -> None:
    """``remover`` apaga a tarefa do repositório."""
    tarefa = servico.criar(TarefaEntrada(titulo="A"))
    servico.remover(tarefa.id)
    assert servico.listar() == []
