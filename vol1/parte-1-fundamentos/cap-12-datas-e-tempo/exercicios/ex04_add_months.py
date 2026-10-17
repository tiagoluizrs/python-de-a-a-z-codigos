"""Exercício 4: somar N meses sem estourar o dia."""
import datetime as dt


def add_months(day: dt.date, months: int) -> dt.date:
    """Soma ``months`` (pode ser negativo) a ``day``.

    Se o dia não existir no mês de destino, use o último dia do mês.

    >>> add_months(dt.date(2026, 1, 31), 1)
    datetime.date(2026, 2, 28)
    >>> add_months(dt.date(2024, 1, 31), 1)
    datetime.date(2024, 2, 29)
    >>> add_months(dt.date(2026, 3, 31), -1)
    datetime.date(2026, 2, 28)
    >>> add_months(dt.date(2026, 11, 15), 3)
    datetime.date(2027, 2, 15)

    Dica: trabalhe com ``ano * 12 + (mes - 1)`` e use ``divmod``.
    """
    raise NotImplementedError
