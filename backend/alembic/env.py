"""Ambiente do Alembic.

A URL do banco vem das configurações da aplicação (variável DATABASE_URL),
e ``target_metadata`` aponta para os modelos ORM, o que habilita o
``alembic revision --autogenerate``.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine

import app.models  # noqa: F401  (registra os modelos em Base.metadata)
from alembic import context
from app.core.config import get_settings
from app.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera o SQL das migrations sem conectar ao banco (``--sql``)."""
    context.configure(
        url=get_settings().database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica as migrations conectando ao banco.

    Se uma conexão for passada em ``config.attributes`` (como fazem os
    testes de integração), ela é reutilizada.
    """
    conexao = config.attributes.get("connection")
    if conexao is not None:
        context.configure(connection=conexao, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
        return

    engine = create_engine(get_settings().database_url)
    with engine.connect() as conexao:
        context.configure(connection=conexao, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
