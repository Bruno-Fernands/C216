"""Endpoints do recurso ``tarefas`` (CRUD completo)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from app.schemas.tarefa import Tarefa, TarefaAtualizacaoParcial, TarefaEntrada
from app.services.tarefas import (
    TarefaNaoEncontradaError,
    TarefaService,
    get_tarefa_service,
)

router = APIRouter(prefix="/tarefas", tags=["tarefas"])

Servico = Annotated[TarefaService, Depends(get_tarefa_service)]
TarefaId = Annotated[int, Path(ge=1, description="Identificador da tarefa")]


def _nao_encontrada(exc: TarefaNaoEncontradaError) -> HTTPException:
    """Converte o erro de negócio em uma resposta HTTP 404."""
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("", response_model=list[Tarefa])
def listar_tarefas(
    servico: Servico,
    concluida: Annotated[
        bool | None, Query(description="Filtra pelo status de conclusão")
    ] = None,
    limite: Annotated[
        int, Query(ge=1, le=100, description="Quantidade máxima de itens")
    ] = 100,
) -> list[Tarefa]:
    """Lista as tarefas, com filtro e limite opcionais via query string."""
    return servico.listar(concluida=concluida, limite=limite)


@router.get("/{tarefa_id}", response_model=Tarefa)
def obter_tarefa(tarefa_id: TarefaId, servico: Servico) -> Tarefa:
    """Retorna uma tarefa pelo id; responde 404 se ela não existir."""
    try:
        return servico.obter(tarefa_id)
    except TarefaNaoEncontradaError as exc:
        raise _nao_encontrada(exc) from exc


@router.post("", response_model=Tarefa, status_code=status.HTTP_201_CREATED)
def criar_tarefa(dados: TarefaEntrada, servico: Servico) -> Tarefa:
    """Cria uma nova tarefa."""
    return servico.criar(dados)


@router.put("/{tarefa_id}", response_model=Tarefa)
def substituir_tarefa(
    tarefa_id: TarefaId, dados: TarefaEntrada, servico: Servico
) -> Tarefa:
    """Substitui todos os campos de uma tarefa existente."""
    try:
        return servico.substituir(tarefa_id, dados)
    except TarefaNaoEncontradaError as exc:
        raise _nao_encontrada(exc) from exc


@router.patch("/{tarefa_id}", response_model=Tarefa)
def atualizar_tarefa(
    tarefa_id: TarefaId, dados: TarefaAtualizacaoParcial, servico: Servico
) -> Tarefa:
    """Atualiza apenas os campos enviados de uma tarefa existente."""
    try:
        return servico.atualizar(tarefa_id, dados)
    except TarefaNaoEncontradaError as exc:
        raise _nao_encontrada(exc) from exc


@router.delete("/{tarefa_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_tarefa(tarefa_id: TarefaId, servico: Servico) -> Response:
    """Remove uma tarefa; responde 204 sem corpo em caso de sucesso."""
    try:
        servico.remover(tarefa_id)
    except TarefaNaoEncontradaError as exc:
        raise _nao_encontrada(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
