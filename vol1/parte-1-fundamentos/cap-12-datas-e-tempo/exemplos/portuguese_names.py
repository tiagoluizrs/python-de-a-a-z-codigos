"""Datas em português do Brasil sem depender do locale do SO."""
import datetime as dt

MONTHS = (
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
)
WEEKDAYS = (   # índice = date.weekday(): segunda = 0
    "segunda-feira", "terça-feira", "quarta-feira",
    "quinta-feira", "sexta-feira", "sábado", "domingo",
)


def format_long(day: dt.date) -> str:
    """12 de outubro de 2026 (segunda-feira)."""
    return (f"{day.day} de {MONTHS[day.month - 1]} de {day.year} "
            f"({WEEKDAYS[day.weekday()]})")


def format_br(moment: dt.datetime) -> str:
    return moment.strftime("%d/%m/%Y %H:%M")   # só diretivas numéricas


def parse_br(text: str) -> dt.date:
    return dt.datetime.strptime(text, "%d/%m/%Y").date()


day = dt.date(2026, 10, 12)
print(format_long(day))
print(format_br(dt.datetime(2026, 10, 12, 9, 5)))
print(parse_br("05/03/2026"))
print(parse_br("05/03/2026").month)   # 3: dia/mês/ano, não mês/dia
