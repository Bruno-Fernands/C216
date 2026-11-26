"""Acesso aos dados das tabelas ``produtos`` e ``movimentacoes``."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.produto import MovimentacaoModel, ProdutoModel


class ProdutoRepository:
    """Operações de persistência de produtos e movimentações."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def listar(
        self, busca: str | None = None, abaixo_do_minimo: bool = False
    ) -> list[ProdutoModel]:
        """Lista os produtos por nome, com busca e filtro opcionais."""
        consulta = select(ProdutoModel).order_by(ProdutoModel.nome)
        if busca:
            consulta = consulta.where(ProdutoModel.nome.ilike(f"%{busca}%"))
        if abaixo_do_minimo:
            consulta = consulta.where(
                ProdutoModel.quantidade < ProdutoModel.estoque_minimo
            )
        return list(self.session.scalars(consulta))

    def obter(self, produto_id: int, bloquear: bool = False) -> ProdutoModel | None:
        """Busca um produto; ``bloquear`` trava a linha até o commit."""
        return self.session.get(ProdutoModel, produto_id, with_for_update=bloquear)

    def obter_por_nome(self, nome: str) -> ProdutoModel | None:
        """Busca um produto pelo nome, sem diferenciar maiúsculas."""
        consulta = select(ProdutoModel).where(
            func.lower(ProdutoModel.nome) == nome.lower()
        )
        return self.session.scalar(consulta)

    def criar(self, campos: dict[str, Any]) -> ProdutoModel:
        """Insere um novo produto e devolve a linha persistida."""
        produto = ProdutoModel(**campos)
        self.session.add(produto)
        self.session.commit()
        self.session.refresh(produto)
        return produto

    def atualizar(self, produto: ProdutoModel, campos: dict[str, Any]) -> ProdutoModel:
        """Altera os campos informados de um produto existente."""
        for nome, valor in campos.items():
            setattr(produto, nome, valor)
        self.session.commit()
        self.session.refresh(produto)
        return produto

    def remover(self, produto: ProdutoModel) -> None:
        """Apaga o produto (e, em cascata, suas movimentações)."""
        self.session.delete(produto)
        self.session.commit()

    def listar_movimentacoes(self, produto_id: int) -> list[MovimentacaoModel]:
        """Histórico do produto, da movimentação mais recente para a mais antiga."""
        consulta = (
            select(MovimentacaoModel)
            .where(MovimentacaoModel.produto_id == produto_id)
            .order_by(MovimentacaoModel.id.desc())
        )
        return list(self.session.scalars(consulta))

    def registrar_movimentacao(
        self, produto: ProdutoModel, campos: dict[str, Any], novo_saldo: int
    ) -> MovimentacaoModel:
        """Grava a movimentação e o novo saldo na mesma transação."""
        movimentacao = MovimentacaoModel(produto_id=produto.id, **campos)
        produto.quantidade = novo_saldo
        self.session.add(movimentacao)
        self.session.commit()
        self.session.refresh(movimentacao)
        return movimentacao

    def resumo(self) -> dict[str, Any]:
        """Totais do estoque calculados pelo banco."""
        linha = self.session.execute(
            select(
                func.count(ProdutoModel.id),
                func.coalesce(func.sum(ProdutoModel.quantidade), 0),
                func.coalesce(
                    func.sum(ProdutoModel.quantidade * ProdutoModel.preco), 0
                ),
                func.count(ProdutoModel.id).filter(
                    ProdutoModel.quantidade < ProdutoModel.estoque_minimo
                ),
            )
        ).one()
        return {
            "total_produtos": linha[0],
            "total_unidades": linha[1],
            "valor_total": linha[2],
            "abaixo_do_minimo": linha[3],
        }
