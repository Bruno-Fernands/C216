"""Classe base declarativa dos modelos ORM."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base de todos os modelos ORM; ``Base.metadata`` é usado pelo Alembic."""
