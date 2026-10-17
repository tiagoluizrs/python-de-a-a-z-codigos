"""O módulo calendar: meses, bissextos e dias da semana."""
import calendar
import datetime as dt

print(calendar.isleap(2024), calendar.isleap(1900), calendar.isleap(2000))
print("bissextos 2000-2029:", calendar.leapdays(2000, 2030))

weekday_first, days = calendar.monthrange(2026, 2)
print("fev/2026:", days, "dias; começa em", weekday_first,
      "(segunda=0)")
print("fev/2028:", calendar.monthrange(2028, 2)[1], "dias")

print(calendar.weekday(2026, 10, 12), calendar.MONDAY)
print(repr(calendar.Day.MONDAY), repr(calendar.Month.OCTOBER))

print(calendar.month(2026, 10))

# Semanas como listas de dias (0 = dia fora do mês).
cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
for week in cal.monthdayscalendar(2026, 10):
    print(week)

# Todas as sextas-feiras 13 de 2026.
print([f"{m:02}/2026" for m in range(1, 13)
       if dt.date(2026, m, 13).weekday() == calendar.FRIDAY])
