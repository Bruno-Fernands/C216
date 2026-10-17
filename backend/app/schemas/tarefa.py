"""Modelos Pydantic do recurso ``tarefas``.

São independentes dos modelos ORM (``app.models``): definem o contrato
da API, enquanto o ORM define a tabela.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TarefaEntrada(BaseModel):
    """Dados enviados pelo cliente para criar (POST) ou substituir (PUT)."""

    titulo: str = Field(min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=500)
    concluida: bool = False


class TarefaAtualizacaoParcial(BaseModel):
    """Dados do PATCH: todos os campos são opcionais."""

    titulo: str | None = Field(default=None, min_length=1, max_length=100)
    descricao: str | None = Field(default=None, max_length=500)
    concluida: bool | None = None

    @field_validator("titulo", "concluida")
    @classmethod
    def nao_aceita_nulo(cls, valor: str | bool | None) -> str | bool:
        """Campos podem ser omitidos, mas não enviados como ``null``."""
        if valor is None:
            raise ValueError("não pode ser nulo")
        return valor


class Tarefa(TarefaEntrada):
    """Tarefa como é devolvida pela API.

    ``from_attributes`` permite criar o schema a partir de um ``TarefaModel``.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    criada_em: datetime
