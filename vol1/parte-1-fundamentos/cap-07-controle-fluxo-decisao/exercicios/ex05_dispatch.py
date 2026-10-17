"""Exercício 5: converter um if/elif longo em despacho por dicionário."""


def convert_slow(value: float, unit: str) -> float:
    """Versão original (NÃO altere): converte para metros."""
    if unit == "km":
        return value * 1000
    elif unit == "m":
        return value
    elif unit == "cm":
        return value / 100
    elif unit == "mm":
        return value / 1000
    elif unit == "mi":
        return value * 1609.344
    else:
        raise ValueError(f"unknown unit: {unit!r}")


# Para o aluno: crie a tabela (unidade -> fator para metros).
FACTORS: dict[str, float] = {}


def convert(value: float, unit: str) -> float:
    """Mesmo comportamento de ``convert_slow``, usando ``FACTORS``.

    Unidade desconhecida -> ``ValueError`` (não deixe ``KeyError``
    escapar). Dica: ``FACTORS.get(unit)`` ou ``try/except KeyError``.
    """
    raise NotImplementedError
