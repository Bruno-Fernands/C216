"""Fixtures dos testes de integração.

Os testes usam um PostgreSQL real, em um banco separado do de
desenvolvimento (``TEST_DATABASE_URL``). O banco é criado se não existir,
o schema é montado aplicando as migrations do Alembic e a tabela é
esvaziada antes de cada teste.
"""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, make_url, text
from sqlalchemy.orm import Session, sessionmaker

from alembic import command
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://c216:c216@localhost:5432/c216_test",
)
BACKEND_DIR = Path(__file__).resolve().parents[2]


def _criar_banco_se_necessario(url: str) -> None:
    """Cria o banco de teste conectando ao banco administrativo ``postgres``."""
    url_obj = make_url(url)
    admin = create_engine(
        url_obj.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    with admin.connect() as conexao:
        existe = conexao.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :nome"),
            {"nome": url_obj.database},
        )
        if not existe:
            conexao.execute(text(f'CREATE DATABASE "{url_obj.database}"'))
    admin.dispose()


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """Engine do banco de teste com todas as migrations aplicadas."""
    _criar_banco_se_necessario(TEST_DATABASE_URL)
    engine = create_engine(TEST_DATABASE_URL)
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    with engine.begin() as conexao:
        config.attributes["connection"] = conexao
        command.upgrade(config, "head")
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(engine: Engine) -> sessionmaker[Session]:
    """Fábrica de sessões com a tabela ``tarefas`` vazia e ids reiniciados."""
    with engine.begin() as conexao:
        conexao.execute(text("TRUNCATE TABLE tarefas RESTART IDENTITY"))
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def session(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    """Sessão do banco de teste."""
    with session_factory() as session:
        yield session


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    """Cliente de teste da aplicação ligado ao banco de teste.

    Assim como em produção, cada requisição recebe uma sessão nova.
    """

    def get_db_teste() -> Iterator[Session]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = get_db_teste
    yield TestClient(app)
    app.dependency_overrides.clear()
