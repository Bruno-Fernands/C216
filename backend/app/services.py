"""Funções de negócio reutilizáveis pelo backend.

Mantidas fora da camada HTTP para facilitar a escrita de testes
unitários (previsto para a Prática 3).
"""


def somar(a: float, b: float) -> float:
    """Soma dois números."""
    return a + b


def dividir(a: float, b: float) -> float:
    """Divide dois números.

    Levanta ``ValueError`` quando o divisor é zero, para que a camada
    HTTP converta o erro em uma resposta apropriada.
    """
    if b == 0:
        raise ValueError("Não é possível dividir por zero.")
    return a / b


def saudacao(nome: str) -> str:
    """Retorna uma saudação personalizada para ``nome``."""
    nome = nome.strip().title()
    return f"Olá, {nome}!"