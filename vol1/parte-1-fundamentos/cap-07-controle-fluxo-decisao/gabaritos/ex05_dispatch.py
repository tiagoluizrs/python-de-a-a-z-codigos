"""Gabarito 5: if/elif convertido em tabela de fatores."""


def convert_slow(value: float, unit: str) -> float:
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


# Os dados ficam numa tabela; a lógica vira uma só multiplicação.
# Dividir por 100 e multiplicar por 0.01 podem diferir na última
# casa decimal: os testes comparam com pytest.approx.
FACTORS: dict[str, float] = {
    "km": 1000, "m": 1, "cm": 0.01, "mm": 0.001, "mi": 1609.344,
}


def convert(value: float, unit: str) -> float:
    factor = FACTORS.get(unit)
    if factor is None:
        raise ValueError(f"unknown unit: {unit!r}")
    return value * factor
