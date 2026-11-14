"""Testes de integração do ``TarefaRepository`` contra o PostgreSQL."""

from sqlalchemy import Engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

from app.repositories.tarefa_repository import TarefaRepository


def test_migration_criou_tabela_tarefas(engine: Engine) -> None:
    """A migration do Alembic cria a tabela com as colunas do modelo ORM."""
    colunas = {c["name"] for c in inspect(engine).get_columns("tarefas")}
    assert colunas == {"id", "titulo", "descricao", "concluida", "criada_em"}


def test_criar_usa_valores_padrao_do_banco(session: Session) -> None:
    """``id`` e ``criada_em`` são preenchidos pelo PostgreSQL."""
    tarefa = TarefaRepository(session).criar({"titulo": "A"})
    assert tarefa.id == 1
    assert tarefa.concluida is False
    assert tarefa.criada_em is not None


def test_dados_persistem_entre_sessoes(
    session_factory: sessionmaker[Session],
) -> None:
    """O que foi gravado em uma sessão é lido por outra (commit no banco)."""
    with session_factory() as primeira:
        criada = TarefaRepository(primeira).criar({"titulo": "Persistida"})

    with session_factory() as segunda:
        lida = TarefaRepository(segunda).obter(criada.id)

    assert lida is not None
    assert lida.titulo == "Persistida"


def test_listar_ordena_filtra_e_limita(session: Session) -> None:
    """``listar`` devolve por id, aplicando filtro e limite no SQL."""
    repositorio = TarefaRepository(session)
    for titulo, concluida in [("A", False), ("B", True), ("C", False)]:
        repositorio.criar({"titulo": titulo, "concluida": concluida})

    assert [t.titulo for t in repositorio.listar()] == ["A", "B", "C"]
    assert [t.titulo for t in repositorio.listar(concluida=False)] == ["A", "C"]
    assert [t.titulo for t in repositorio.listar(limite=2)] == ["A", "B"]


def test_atualizar_e_remover(session: Session, engine: Engine) -> None:
    """``atualizar`` grava as alterações e ``remover`` apaga a linha."""
    repositorio = TarefaRepository(session)
    tarefa = repositorio.criar({"titulo": "A"})

    repositorio.atualizar(tarefa, {"concluida": True})
    with engine.connect() as conexao:
        concluida = conexao.scalar(
            text("SELECT concluida FROM tarefas WHERE id = :id"), {"id": tarefa.id}
        )
    assert concluida is True

    repositorio.remover(tarefa)
    assert repositorio.obter(tarefa.id) is None
