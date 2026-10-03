"""Modelos Pydantic do recurso ``tarefas``."""

from pydantic import BaseModel, Field


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


class Tarefa(TarefaEntrada):
    """Tarefa como é armazenada e devolvida pela API."""

    id: int
