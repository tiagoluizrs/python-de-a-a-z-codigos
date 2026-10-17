"""Exercício 1: idade exata em anos, meses e dias."""
import datetime as dt


def exact_age(born: dt.date, today: dt.date) -> tuple[int, int, int]:
    """Devolve ``(anos, meses, dias)`` completos entre as duas datas.

    Regras:
    - Conte meses completos: o maior número de meses ``m`` tal que
      ``born + m meses <= today``, onde somar meses "gruda" o dia no
      último dia válido do mês (31/01 + 1 mês = 28/02 em 2026).
    - Os dias são o que sobra depois dos meses completos.
    - anos = m // 12 e meses = m % 12.
    - Se ``today < born``, levante ``ValueError``.

    Exemplos:
    >>> exact_age(dt.date(1990, 3, 25), dt.date(2026, 10, 12))
    (36, 6, 17)
    >>> exact_age(dt.date(2024, 2, 29), dt.date(2025, 2, 28))
    (1, 0, 0)

    Dica: ``calendar.monthrange(ano, mes)[1]`` dá o último dia do mês.
    """
    raise NotImplementedError
