"""Testes unitários das funções de negócio em ``app.services``."""

import pytest

from app.services import dividir, saudacao, somar


@pytest.fixture
def valores() -> tuple[float, float]:
    """Fixture com valores usados nas operações de negócio."""
    return (4.0, 2.0)


@pytest.mark.parametrize(
    "a,b,esperado",
    [
        (2, 3, 5),
        (-1, 1, 0),
        (2.5, 2.5, 5.0),
        (0, 0, 0),
    ],
)
def test_somar(a: float, b: float, esperado: float) -> None:
    """Testa a soma de dois números (parametrizado)."""
    assert somar(a, b) == esperado


def test_somar_com_fixture(valores: tuple[float, float]) -> None:
    """Testa a soma usando valores fornecidos pela fixture."""
    a, b = valores
    assert somar(a, b) == 6.0


@pytest.mark.parametrize(
    "a,b,esperado",
    [
        (10, 2, 5.0),
        (9, 3, 3.0),
        (7, 2, 3.5),
    ],
)
def test_dividir(a: float, b: float, esperado: float) -> None:
    """Testa a divisão de dois números (parametrizado)."""
    assert dividir(a, b) == esperado


@pytest.mark.parametrize("a,b", [(1, 0), (-5, 0), (0, 0)])
def test_dividir_por_zero_levanta_erro(a: float, b: float) -> None:
    """Testa o caso de erro: divisão por zero deve levantar ``ValueError``."""
    with pytest.raises(ValueError, match="dividir por zero"):
        dividir(a, b)


@pytest.mark.parametrize(
    "entrada,esperado",
    [
        ("bruno", "Olá, Bruno!"),
        (" matheus ", "Olá, Matheus!"),
        ("ANA", "Olá, Ana!"),
    ],
)
def test_saudacao(entrada: str, esperado: str) -> None:
    """Testa a saudação personalizada (parametrizado)."""
    assert saudacao(entrada) == esperado


def test_saudacao_com_nome_vazio() -> None:
    """Caso de borda: um nome vazio/em branco ainda gera uma saudação."""
    assert saudacao("   ") == "Olá, !"