"""Testes unitários das regras de negócio em ``app.services.tarefas``."""

import pytest

from app.schemas.tarefa import TarefaAtualizacaoParcial, TarefaEntrada
from app.services.tarefas import (
    TarefaNaoEncontradaError,
    TarefaService,
    get_tarefa_service,
)


@pytest.fixture
def servico() -> TarefaService:
    """Fixture com um serviço vazio para cada teste."""
    return TarefaService()


def test_criar_gera_ids_sequenciais(servico: TarefaService) -> None:
    """Cada tarefa criada recebe o próximo id."""
    primeira = servico.criar(TarefaEntrada(titulo="A"))
    segunda = servico.criar(TarefaEntrada(titulo="B"))
    assert (primeira.id, segunda.id) == (1, 2)
    assert primeira.concluida is False


def test_id_nao_e_reaproveitado_apos_remocao(servico: TarefaService) -> None:
    """Remover uma tarefa não libera o id dela para a próxima."""
    primeira = servico.criar(TarefaEntrada(titulo="A"))
    servico.remover(primeira.id)
    assert servico.criar(TarefaEntrada(titulo="B")).id == 2


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
        (False, 1, ["A"]),
    ],
)
def test_listar_com_filtro_e_limite(
    servico: TarefaService, concluida: bool | None, limite: int, esperado: list[str]
) -> None:
    """``listar`` aplica o filtro por status e depois o limite."""
    servico.criar(TarefaEntrada(titulo="A"))
    servico.criar(TarefaEntrada(titulo="B", concluida=True))
    servico.criar(TarefaEntrada(titulo="C"))
    tarefas = servico.listar(concluida=concluida, limite=limite)
    assert [t.titulo for t in tarefas] == esperado


def test_substituir_redefine_campos_omitidos(servico: TarefaService) -> None:
    """``substituir`` troca a tarefa inteira, mantendo apenas o id."""
    tarefa = servico.criar(TarefaEntrada(titulo="A", descricao="x", concluida=True))
    nova = servico.substituir(tarefa.id, TarefaEntrada(titulo="B"))
    assert nova.model_dump() == {
        "id": tarefa.id,
        "titulo": "B",
        "descricao": None,
        "concluida": False,
    }
    assert servico.obter(tarefa.id) == nova


def test_atualizar_altera_apenas_campos_enviados(servico: TarefaService) -> None:
    """``atualizar`` preserva os campos que não foram enviados."""
    tarefa = servico.criar(TarefaEntrada(titulo="A", descricao="x"))
    nova = servico.atualizar(tarefa.id, TarefaAtualizacaoParcial(concluida=True))
    assert nova.model_dump() == {
        "id": tarefa.id,
        "titulo": "A",
        "descricao": "x",
        "concluida": True,
    }
    assert servico.obter(tarefa.id) == nova


def test_atualizar_permite_limpar_descricao(servico: TarefaService) -> None:
    """Enviar ``descricao=None`` explicitamente limpa o campo."""
    tarefa = servico.criar(TarefaEntrada(titulo="A", descricao="x"))
    nova = servico.atualizar(tarefa.id, TarefaAtualizacaoParcial(descricao=None))
    assert nova.descricao is None


def test_remover(servico: TarefaService) -> None:
    """``remover`` apaga a tarefa da listagem."""
    tarefa = servico.criar(TarefaEntrada(titulo="A"))
    servico.remover(tarefa.id)
    assert servico.listar() == []


def test_get_tarefa_service_retorna_instancia_unica() -> None:
    """A dependência da aplicação devolve sempre o mesmo serviço."""
    assert get_tarefa_service() is get_tarefa_service()
