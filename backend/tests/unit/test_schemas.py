"""Testes unitários dos modelos Pydantic em ``app.schemas.tarefa``."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.models.tarefa import TarefaModel
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


@pytest.mark.parametrize("campo", ["titulo", "concluida"])
def test_atualizacao_parcial_rejeita_nulo(campo: str) -> None:
    """``titulo`` e ``concluida`` podem ser omitidos, mas não enviados nulos."""
    with pytest.raises(ValidationError, match="não pode ser nulo"):
        TarefaAtualizacaoParcial(**{campo: None})


@pytest.mark.parametrize(
    "campos",
    [
        {"titulo": "Estudar", "criada_em": datetime.now(UTC)},
        {"titulo": "Estudar", "id": 1},
    ],
)
def test_tarefa_exige_id_e_criada_em(campos: dict) -> None:
    """O modelo de saída exige ``id`` e ``criada_em``."""
    with pytest.raises(ValidationError):
        Tarefa(**campos)


def test_tarefa_a_partir_do_modelo_orm() -> None:
    """``from_attributes`` permite converter um ``TarefaModel`` no schema."""
    agora = datetime.now(UTC)
    modelo = TarefaModel(
        id=3, titulo="Estudar", descricao=None, concluida=True, criada_em=agora
    )
    tarefa = Tarefa.model_validate(modelo)
    assert tarefa.model_dump() == {
        "id": 3,
        "titulo": "Estudar",
        "descricao": None,
        "concluida": True,
        "criada_em": agora,
    }
