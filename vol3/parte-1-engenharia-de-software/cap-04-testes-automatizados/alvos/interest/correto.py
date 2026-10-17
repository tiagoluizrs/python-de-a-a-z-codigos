"""Alvo do exercício 3."""


def compound_interest(principal, rate, years, periods=1):
    """Montante com juros compostos: ``principal * (1 + rate/periods) ** (periods*years)``.
    ``rate`` é uma FRAÇÃO (0.05 = 5%). Valores inválidos levantam ``ValueError``."""
    if principal < 0 or years < 0 or rate < 0:
        raise ValueError("principal, rate e years não podem ser negativos")
    if periods < 1:
        raise ValueError("periods deve ser >= 1")
    return principal * (1 + rate / periods) ** (periods * years)
