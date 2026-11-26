"""Endpoints de produtos e de suas movimentações de estoque."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from app.schemas.produto import (
    Movimentacao,
    MovimentacaoEntrada,
    Produto,
    ProdutoEntrada,
    Resumo,
)
from app.services.produtos import (
    EstoqueInsuficienteError,
    ProdutoDuplicadoError,
    ProdutoNaoEncontradoError,
    ProdutoService,
    get_produto_service,
)

router = APIRouter(prefix="/produtos", tags=["produtos"])

Servico = Annotated[ProdutoService, Depends(get_produto_service)]
ProdutoId = Annotated[int, Path(ge=1, description="Identificador do produto")]


def _http(exc: Exception) -> HTTPException:
    """Converte um erro de negócio na resposta HTTP correspondente."""
    codigo = (
        status.HTTP_404_NOT_FOUND
        if isinstance(exc, ProdutoNaoEncontradoError)
        else status.HTTP_409_CONFLICT
    )
    return HTTPException(status_code=codigo, detail=str(exc))


ERROS = (ProdutoNaoEncontradoError, ProdutoDuplicadoError, EstoqueInsuficienteError)


@router.get("", response_model=list[Produto])
def listar_produtos(
    servico: Servico,
    busca: Annotated[
        str | None, Query(max_length=80, description="Trecho do nome")
    ] = None,
    abaixo_do_minimo: Annotated[
        bool, Query(description="Só produtos abaixo do estoque mínimo")
    ] = False,
) -> list[Produto]:
    """Lista os produtos em ordem alfabética."""
    return servico.listar(busca, abaixo_do_minimo)


@router.get("/resumo", response_model=Resumo)
def obter_resumo(servico: Servico) -> Resumo:
    """Totais do estoque: produtos, unidades, valor e alertas."""
    return servico.resumo()


@router.get("/{produto_id}", response_model=Produto)
def obter_produto(produto_id: ProdutoId, servico: Servico) -> Produto:
    """Retorna um produto pelo id."""
    try:
        return servico.obter(produto_id)
    except ERROS as exc:
        raise _http(exc) from exc


@router.post("", response_model=Produto, status_code=status.HTTP_201_CREATED)
def criar_produto(dados: ProdutoEntrada, servico: Servico) -> Produto:
    """Cadastra um produto com saldo inicial zero."""
    try:
        return servico.criar(dados)
    except ERROS as exc:
        raise _http(exc) from exc


@router.put("/{produto_id}", response_model=Produto)
def atualizar_produto(
    produto_id: ProdutoId, dados: ProdutoEntrada, servico: Servico
) -> Produto:
    """Edita os dados cadastrais do produto."""
    try:
        return servico.atualizar(produto_id, dados)
    except ERROS as exc:
        raise _http(exc) from exc


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_produto(produto_id: ProdutoId, servico: Servico) -> Response:
    """Remove o produto e seu histórico; 204 sem corpo."""
    try:
        servico.remover(produto_id)
    except ERROS as exc:
        raise _http(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{produto_id}/movimentacoes", response_model=list[Movimentacao])
def listar_movimentacoes(produto_id: ProdutoId, servico: Servico) -> list[Movimentacao]:
    """Histórico de entradas e saídas do produto."""
    try:
        return servico.listar_movimentacoes(produto_id)
    except ERROS as exc:
        raise _http(exc) from exc


@router.post(
    "/{produto_id}/movimentacoes",
    response_model=Movimentacao,
    status_code=status.HTTP_201_CREATED,
)
def registrar_movimentacao(
    produto_id: ProdutoId, dados: MovimentacaoEntrada, servico: Servico
) -> Movimentacao:
    """Registra uma entrada ou saída; 409 se a saída exceder o saldo."""
    try:
        return servico.movimentar(produto_id, dados)
    except ERROS as exc:
        raise _http(exc) from exc
