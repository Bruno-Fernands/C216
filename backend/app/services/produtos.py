"""Regras de negócio do controle de estoque.

O serviço não acessa o banco diretamente: delega a persistência ao
``ProdutoRepository`` e devolve schemas Pydantic, nunca modelos ORM.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.produto import ProdutoModel
from app.repositories.produto_repository import ProdutoRepository
from app.schemas.produto import (
    Movimentacao,
    MovimentacaoEntrada,
    Produto,
    ProdutoEntrada,
    Resumo,
)


class ProdutoNaoEncontradoError(Exception):
    """O id informado não corresponde a nenhum produto."""

    def __init__(self, produto_id: int) -> None:
        super().__init__(f"Produto {produto_id} não encontrado.")


class ProdutoDuplicadoError(Exception):
    """Já existe outro produto com o mesmo nome."""

    def __init__(self, nome: str) -> None:
        super().__init__(f"Já existe um produto com o nome '{nome}'.")


class EstoqueInsuficienteError(Exception):
    """A saída pedida é maior que o saldo disponível."""

    def __init__(self, disponivel: int, pedido: int) -> None:
        super().__init__(
            f"Estoque insuficiente: disponível {disponivel}, solicitado {pedido}."
        )


class ProdutoService:
    """CRUD de produtos e movimentações de estoque."""

    def __init__(self, repositorio: ProdutoRepository) -> None:
        self.repositorio = repositorio

    def _buscar(self, produto_id: int, bloquear: bool = False) -> ProdutoModel:
        produto = self.repositorio.obter(produto_id, bloquear=bloquear)
        if produto is None:
            raise ProdutoNaoEncontradoError(produto_id)
        return produto

    def _garantir_nome_livre(self, nome: str, produto_id: int | None = None) -> None:
        existente = self.repositorio.obter_por_nome(nome)
        if existente is not None and existente.id != produto_id:
            raise ProdutoDuplicadoError(nome)

    def listar(
        self, busca: str | None = None, abaixo_do_minimo: bool = False
    ) -> list[Produto]:
        """Lista os produtos com busca por nome e filtro de estoque baixo."""
        produtos = self.repositorio.listar(busca, abaixo_do_minimo)
        return [Produto.model_validate(p) for p in produtos]

    def obter(self, produto_id: int) -> Produto:
        """Retorna o produto ou levanta ``ProdutoNaoEncontradoError``."""
        return Produto.model_validate(self._buscar(produto_id))

    def criar(self, dados: ProdutoEntrada) -> Produto:
        """Cria um produto com saldo zero; o nome deve ser único."""
        self._garantir_nome_livre(dados.nome)
        return Produto.model_validate(self.repositorio.criar(dados.model_dump()))

    def atualizar(self, produto_id: int, dados: ProdutoEntrada) -> Produto:
        """Edita os dados cadastrais (o saldo não muda por aqui)."""
        produto = self._buscar(produto_id)
        self._garantir_nome_livre(dados.nome, produto_id)
        return Produto.model_validate(
            self.repositorio.atualizar(produto, dados.model_dump())
        )

    def remover(self, produto_id: int) -> None:
        """Remove o produto e todo o seu histórico."""
        self.repositorio.remover(self._buscar(produto_id))

    def listar_movimentacoes(self, produto_id: int) -> list[Movimentacao]:
        """Histórico de movimentações de um produto existente."""
        self._buscar(produto_id)
        movimentacoes = self.repositorio.listar_movimentacoes(produto_id)
        return [Movimentacao.model_validate(m) for m in movimentacoes]

    def movimentar(self, produto_id: int, dados: MovimentacaoEntrada) -> Movimentacao:
        """Registra entrada ou saída; a saída não pode deixar o saldo negativo."""
        # Linha travada: duas saídas simultâneas não usam o mesmo saldo.
        produto = self._buscar(produto_id, bloquear=True)
        if dados.tipo == "entrada":
            novo_saldo = produto.quantidade + dados.quantidade
        else:
            if dados.quantidade > produto.quantidade:
                raise EstoqueInsuficienteError(produto.quantidade, dados.quantidade)
            novo_saldo = produto.quantidade - dados.quantidade
        movimentacao = self.repositorio.registrar_movimentacao(
            produto, dados.model_dump(), novo_saldo
        )
        return Movimentacao.model_validate(movimentacao)

    def resumo(self) -> Resumo:
        """Indicadores gerais do estoque."""
        return Resumo(**self.repositorio.resumo())


def get_produto_service(
    session: Annotated[Session, Depends(get_db)],
) -> ProdutoService:
    """Dependência do FastAPI: serviço ligado à sessão da requisição."""
    return ProdutoService(ProdutoRepository(session))
