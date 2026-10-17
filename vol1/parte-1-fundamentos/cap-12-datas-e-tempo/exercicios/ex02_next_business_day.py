"""Exercício 2: próximo dia útil, com feriados fornecidos."""
import datetime as dt


def next_business_day(day: dt.date, holidays: set[dt.date]) -> dt.date:
    """Primeiro dia útil ESTRITAMENTE depois de ``day``.

    Dia útil = de segunda a sexta e fora do conjunto ``holidays``.

    Exemplos (2026-10-09 é sexta, 2026-10-12 é segunda):
    >>> next_business_day(dt.date(2026, 10, 9), set())
    datetime.date(2026, 10, 12)
    >>> next_business_day(dt.date(2026, 10, 9), {dt.date(2026, 10, 12)})
    datetime.date(2026, 10, 13)

    Dica: ``date.weekday()`` devolve 0 para segunda e 6 para domingo.
    """
    raise NotImplementedError


def add_business_days(day: dt.date, count: int,
                      holidays: set[dt.date]) -> dt.date:
    """Avança ``count`` dias úteis (``count >= 0``).

    ``count == 0`` devolve o próprio ``day`` (mesmo que não seja útil).
    Se ``count < 0``, levante ``ValueError``.
    """
    raise NotImplementedError
