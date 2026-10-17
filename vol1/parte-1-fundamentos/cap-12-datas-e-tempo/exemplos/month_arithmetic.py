"""Aritmética de meses: Python puro e dateutil.relativedelta."""
import calendar
import datetime as dt

from dateutil.relativedelta import relativedelta


def add_months(day: dt.date, months: int) -> dt.date:
    """Soma meses e 'gruda' o dia no último dia válido do mês."""
    index = day.year * 12 + (day.month - 1) + months
    year, month0 = divmod(index, 12)
    month = month0 + 1
    last_day = calendar.monthrange(year, month)[1]
    return dt.date(year, month, min(day.day, last_day))


def last_day_of_month(day: dt.date) -> dt.date:
    last = calendar.monthrange(day.year, day.month)[1]
    return day.replace(day=last)


jan31 = dt.date(2026, 1, 31)
print("Jan 31 + 1 mês :", add_months(jan31, 1))
print("Jan 31 + 2 meses:", add_months(jan31, 2))
print("Jan 31 - 2 meses:", add_months(jan31, -2))
print("2024-02-29 + 12 :", add_months(dt.date(2024, 2, 29), 12))
print("fim do mês      :", last_day_of_month(dt.date(2028, 2, 10)))

# Armadilhas de quem tenta com replace:
try:
    jan31.replace(month=2)
except ValueError as error:
    print("replace:", error)

print("--- relativedelta ---")
print(jan31 + relativedelta(months=1))
print(jan31 + relativedelta(months=+1, days=+1))
print(dt.date(2024, 2, 29) + relativedelta(years=1))
print(dt.date(2026, 10, 12) + relativedelta(day=31))   # absoluto
print(relativedelta(dt.date(2026, 10, 12), dt.date(1990, 3, 25)))

# Idade em anos completos.
born = dt.date(1990, 3, 25)
today = dt.date(2026, 10, 12)
years = today.year - born.year - ((today.month, today.day)
                                  < (born.month, born.day))
print("idade:", years, "|", relativedelta(today, born).years)

# Diferença em dias não é diferença em meses:
print((dt.date(2026, 3, 1) - dt.date(2026, 2, 1)).days,
      (dt.date(2026, 4, 1) - dt.date(2026, 3, 1)).days)
