"""Exercício 3: SLO, orçamento de erro e alerta de queima em duas janelas."""


def error_budget(total: int, slo: float) -> float:
    """Quantas requisições RUINS a meta tolera em ``total`` requisições: ``total * (1 - slo)``. ``slo`` precisa estar
    em ``(0, 1)``; fora disso, ``ValueError``. ``total`` negativo: ``ValueError``."""
    raise NotImplementedError


def budget_spent(bad: int, total: int, slo: float) -> float:
    """Fração do orçamento já gasta: ``bad / error_budget(total, slo)`` (``0.72`` = 72%). Pode passar de ``1.0``.
    Com ``total == 0``: ``0.0``."""
    raise NotImplementedError


def burn_rate(bad: int, total: int, slo: float) -> float:
    """Velocidade de queima: a taxa de erro observada dividida pela taxa tolerada, ``(bad / total) / (1 - slo)``.
    ``1.0`` esgota o orçamento exatamente no fim da janela do SLO. Com ``total == 0``: ``0.0``. ``bad > total`` ou
    valores negativos: ``ValueError``."""
    raise NotImplementedError


def days_to_exhaustion(rate: float, window_days: float = 30.0) -> float:
    """Em quantos dias o orçamento acaba se a queima continuar em ``rate``: ``window_days / rate``; ``float('inf')`` se
    ``rate <= 0``."""
    raise NotImplementedError


def should_page(windows: list[tuple[int, int]], slo: float, threshold: float = 14.4) -> bool:
    """Alerta de várias janelas: ``windows`` é uma lista de ``(bad, total)`` (ex.: 5 min e 1 h). Só devolve ``True`` se
    a queima de TODAS as janelas for ``>= threshold``. Lista vazia: ``ValueError``."""
    raise NotImplementedError


def allowed_downtime_minutes(slo: float, window_days: float = 30.0) -> float:
    """Minutos de indisponibilidade que o SLO tolera na janela (``99.9%`` em 30 dias dá ``43.2``)."""
    raise NotImplementedError
