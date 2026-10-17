"""Gabarito do exercício 4."""
import calendar
import datetime as dt


def add_months(day: dt.date, months: int) -> dt.date:
    # Um "índice de mês" contínuo transforma a soma em aritmética de int.
    index = day.year * 12 + (day.month - 1) + months
    year, month0 = divmod(index, 12)   # divmod funciona com negativos
    month = month0 + 1
    last_day = calendar.monthrange(year, month)[1]
    return dt.date(year, month, min(day.day, last_day))
