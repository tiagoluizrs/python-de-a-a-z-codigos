"""Gabarito do exercício 1."""
import calendar
import datetime as dt


def _add_months(day: dt.date, months: int) -> dt.date:
    index = day.year * 12 + (day.month - 1) + months
    year, month0 = divmod(index, 12)
    month = month0 + 1
    last = calendar.monthrange(year, month)[1]
    return dt.date(year, month, min(day.day, last))


def exact_age(born: dt.date, today: dt.date) -> tuple[int, int, int]:
    if today < born:
        raise ValueError("today is before the birth date")
    # Estimativa por cima da quantidade de meses e ajuste para baixo.
    months = (today.year - born.year) * 12 + (today.month - born.month)
    while _add_months(born, months) > today:
        months -= 1
    anchor = _add_months(born, months)
    days = (today - anchor).days
    return months // 12, months % 12, days
