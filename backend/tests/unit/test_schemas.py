"""Testes unitários dos modelos Pydantic em ``app.schemas.tarefa``."""

import pytest
from pydantic import ValidationError

from app.schemas.tarefa import Tarefa, TarefaAtualizacaoParcial, TarefaEntrada


def test_tarefa_entrada_valores_padrao() -> None:
    """Apenas ``titulo`` é obrigatório; os demais campos têm padrão."""
    tarefa = TarefaEntrada(titulo="Estudar")
    assert tarefa.descricao is None
    assert tarefa.concluida is False


@pytest.mark.parametrize(
    "campos",
    [
        {},
        {"titulo": ""},
        {"titulo": "x" * 101},
        {"titulo": "ok", "descricao": "x" * 501},
    ],
)
def test_tarefa_entrada_invalida(campos: dict) -> None:
    """Título ausente/vazio/longo ou descrição longa são rejeitados."""
    with pytest.raises(ValidationError):
        TarefaEntrada(**campos)


def test_atualizacao_parcial_registra_apenas_campos_enviados() -> None:
    """``exclude_unset`` distingue campo omitido de campo enviado."""
    dados = TarefaAtualizacaoParcial(concluida=True)
    assert dados.model_dump(exclude_unset=True) == {"concluida": True}


def test_atualizacao_parcial_rejeita_titulo_vazio() -> None:
    """Quando enviado, o título segue a mesma validação da criação."""
    with pytest.raises(ValidationError):
        TarefaAtualizacaoParcial(titulo="")


def test_tarefa_exige_id() -> None:
    """O modelo de saída exige o ``id``."""
    with pytest.raises(ValidationError):
        Tarefa(titulo="Estudar")
