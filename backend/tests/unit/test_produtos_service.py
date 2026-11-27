"""Testes unitários das regras de negócio em ``app.services.produtos``.

O ``ProdutoRepository`` é substituído por um repositório falso em memória,
então estes testes não precisam de banco de dados.
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import pytest
from pydantic import ValidationError

from app.models.produto import MovimentacaoModel, ProdutoModel
from app.schemas.produto import MovimentacaoEntrada, ProdutoEntrada
from app.services.produtos import (
    EstoqueInsuficienteError,
    ProdutoDuplicadoError,
    ProdutoNaoEncontradoError,
    ProdutoService,
)


class RepositorioFalso:
    """Implementa a mesma interface do ``ProdutoRepository`` em memória."""

    def __init__(self) -> None:
        self.produtos: dict[int, ProdutoModel] = {}
        self.movimentacoes: list[MovimentacaoModel] = []

    def listar(self, busca=None, abaixo_do_minimo=False) -> list[ProdutoModel]:
        produtos = sorted(self.produtos.values(), key=lambda p: p.nome)
        if busca:
            produtos = [p for p in produtos if busca.lower() in p.nome.lower()]
        if abaixo_do_minimo:
            produtos = [p for p in produtos if p.quantidade < p.estoque_minimo]
        return produtos

    def obter(self, produto_id: int, bloquear: bool = False) -> ProdutoModel | None:
        return self.produtos.get(produto_id)

    def obter_por_nome(self, nome: str) -> ProdutoModel | None:
        return next(
            (p for p in self.produtos.values() if p.nome.lower() == nome.lower()),
            None,
        )

    def criar(self, campos: dict[str, Any]) -> ProdutoModel:
        produto = ProdutoModel(
            id=len(self.produtos) + 1,
            quantidade=0,
            criado_em=datetime.now(UTC),
            **campos,
        )
        self.produtos[produto.id] = produto
        return produto

    def atualizar(self, produto: ProdutoModel, campos: dict[str, Any]) -> ProdutoModel:
        for nome, valor in campos.items():
            setattr(produto, nome, valor)
        return produto

    def remover(self, produto: ProdutoModel) -> None:
        del self.produtos[produto.id]

    def listar_movimentacoes(self, produto_id: int) -> list[MovimentacaoModel]:
        return [m for m in self.movimentacoes if m.produto_id == produto_id]

    def registrar_movimentacao(self, produto, campos, novo_saldo):
        movimentacao = MovimentacaoModel(
            id=len(self.movimentacoes) + 1,
            produto_id=produto.id,
            criada_em=datetime.now(UTC),
            **campos,
        )
        produto.quantidade = novo_saldo
        self.movimentacoes.append(movimentacao)
        return movimentacao


@pytest.fixture
def servico() -> ProdutoService:
    return ProdutoService(RepositorioFalso())


def _produto(nome="Caneta", preco="2.50", minimo=0) -> ProdutoEntrada:
    return ProdutoEntrada(nome=nome, preco=Decimal(preco), estoque_minimo=minimo)


def test_produto_novo_comeca_com_saldo_zero(servico):
    produto = servico.criar(_produto())
    assert produto.quantidade == 0
    assert produto.id == 1


def test_nome_duplicado_ignora_maiusculas(servico):
    servico.criar(_produto("Caneta"))
    with pytest.raises(ProdutoDuplicadoError):
        servico.criar(_produto("CANETA"))


def test_editar_mantendo_o_proprio_nome_e_permitido(servico):
    produto = servico.criar(_produto("Caneta"))
    editado = servico.atualizar(produto.id, _produto("Caneta", preco="3.00"))
    assert editado.preco == Decimal("3.00")


def test_editar_para_nome_de_outro_produto_falha(servico):
    servico.criar(_produto("Caneta"))
    lapis = servico.criar(_produto("Lápis"))
    with pytest.raises(ProdutoDuplicadoError):
        servico.atualizar(lapis.id, _produto("caneta"))


def test_entrada_e_saida_alteram_o_saldo(servico):
    produto = servico.criar(_produto())
    servico.movimentar(produto.id, MovimentacaoEntrada(tipo="entrada", quantidade=10))
    servico.movimentar(produto.id, MovimentacaoEntrada(tipo="saida", quantidade=4))
    assert servico.obter(produto.id).quantidade == 6
    assert len(servico.listar_movimentacoes(produto.id)) == 2


def test_saida_maior_que_o_saldo_e_recusada(servico):
    produto = servico.criar(_produto())
    servico.movimentar(produto.id, MovimentacaoEntrada(tipo="entrada", quantidade=3))
    with pytest.raises(EstoqueInsuficienteError):
        servico.movimentar(produto.id, MovimentacaoEntrada(tipo="saida", quantidade=4))
    assert servico.obter(produto.id).quantidade == 3
    assert len(servico.listar_movimentacoes(produto.id)) == 1


def test_saida_de_todo_o_saldo_zera_o_estoque(servico):
    produto = servico.criar(_produto())
    servico.movimentar(produto.id, MovimentacaoEntrada(tipo="entrada", quantidade=5))
    servico.movimentar(produto.id, MovimentacaoEntrada(tipo="saida", quantidade=5))
    assert servico.obter(produto.id).quantidade == 0


def test_abaixo_do_minimo(servico):
    produto = servico.criar(_produto(minimo=5))
    assert produto.abaixo_do_minimo is True
    servico.movimentar(produto.id, MovimentacaoEntrada(tipo="entrada", quantidade=5))
    assert servico.obter(produto.id).abaixo_do_minimo is False
    assert servico.listar(abaixo_do_minimo=True) == []


def test_operacoes_em_produto_inexistente(servico):
    with pytest.raises(ProdutoNaoEncontradoError):
        servico.obter(99)
    with pytest.raises(ProdutoNaoEncontradoError):
        servico.remover(99)
    with pytest.raises(ProdutoNaoEncontradoError):
        servico.movimentar(99, MovimentacaoEntrada(tipo="entrada", quantidade=1))


@pytest.mark.parametrize(
    "campos",
    [
        {"nome": "X", "preco": "1"},  # nome curto
        {"nome": "Caneta", "preco": "-1"},  # preço negativo
        {"nome": "Caneta", "preco": "1.999"},  # mais de 2 casas
        {"nome": "Caneta", "preco": "1", "estoque_minimo": -1},
    ],
)
def test_validacao_do_produto(campos):
    with pytest.raises(ValidationError):
        ProdutoEntrada(**campos)


@pytest.mark.parametrize(
    "campos",
    [
        {"tipo": "entrada", "quantidade": 0},
        {"tipo": "ajuste", "quantidade": 1},
    ],
)
def test_validacao_da_movimentacao(campos):
    with pytest.raises(ValidationError):
        MovimentacaoEntrada(**campos)
