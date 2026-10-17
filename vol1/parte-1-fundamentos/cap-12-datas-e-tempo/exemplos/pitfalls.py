"""Armadilhas clássicas com datas."""
import datetime as dt
import time
from zoneinfo import ZoneInfo

sp = ZoneInfo("America/Sao_Paulo")

# 1. Meses vão de 1 a 12 (em JavaScript, 0 a 11).
try:
    dt.datetime(2026, 0, 10)
except ValueError as error:
    print("mês 0:", error)

# 2. timedelta não tem meses nem anos.
try:
    dt.timedelta(months=1)
except TypeError as error:
    print("timedelta:", error)

# 3. "Hoje" depende do fuso: o mesmo instante, dois dias.
instant = dt.datetime(2026, 10, 13, 1, 0, tzinfo=dt.UTC)
print("UTC       :", instant.date())
print("São Paulo :", instant.astimezone(sp).date())

# 4. timestamp() de um naive usa o fuso do SISTEMA.
naive = dt.datetime(2026, 10, 12, 9, 0)
print("naive   :", naive.timestamp(), "(depende da máquina)")
print("como UTC:", naive.replace(tzinfo=dt.UTC).timestamp())

# 5. Valor padrão avaliado UMA vez, na definição da função.
def log_bad(message, when=dt.datetime.now()):
    return when

first = log_bad("a")
time.sleep(0.01)
print("padrão congelado:", log_bad("b") == first)


def log_good(message, when=None):
    return when if when is not None else dt.datetime.now(dt.UTC)


print("padrão correto  :", log_good("b") != log_good("c"))

# 6. date + timedelta com horas: a parte de horas é descartada.
print(dt.date(2026, 1, 1) + dt.timedelta(hours=36))

# 7. Diferença de datetimes com o MESMO tzinfo ignora o fuso.
ny = ZoneInfo("America/New_York")
a = dt.datetime(2024, 3, 9, 12, tzinfo=ny)
b = dt.datetime(2024, 3, 10, 12, tzinfo=ny)
print("mesmo fuso   :", b - a)
print("via UTC      :", b.astimezone(dt.UTC) - a.astimezone(dt.UTC))

# 8. replace(year=...) em 29 de fevereiro.
try:
    dt.date(2024, 2, 29).replace(year=2025)
except ValueError as error:
    print("replace:", error)

# 9. %y: o século é escolhido por regra (69-99 -> 19xx).
print(dt.datetime.strptime("30", "%y").year,
      dt.datetime.strptime("70", "%y").year)
