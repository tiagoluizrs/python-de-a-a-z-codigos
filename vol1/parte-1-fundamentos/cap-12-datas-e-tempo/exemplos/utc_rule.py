"""Regra de ouro: armazene em UTC, converta só para exibir."""
import datetime as dt
import warnings
from zoneinfo import ZoneInfo

# Forma moderna de obter "agora" em UTC (aware).
now_utc = dt.datetime.now(dt.UTC)
print(now_utc.tzinfo, dt.UTC is dt.timezone.utc)

# utcnow() devolve um NAIVE e está descontinuado desde o 3.12.
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    old = dt.datetime.utcnow()
print(type(caught[0].message).__name__, "->", caught[0].message)
print("utcnow é aware?", old.tzinfo is not None)

# Epoch: sempre com fuso explícito.
print(dt.datetime.fromtimestamp(0, dt.UTC))
print(dt.datetime.fromtimestamp(0, ZoneInfo("America/Sao_Paulo")))

# O ciclo saudável: entra local -> grava UTC -> exibe local.
sao_paulo = ZoneInfo("America/Sao_Paulo")
tokyo = ZoneInfo("Asia/Tokyo")

typed = dt.datetime(2026, 10, 12, 14, 30, tzinfo=sao_paulo)
stored = typed.astimezone(dt.UTC)           # o que vai ao banco
print("armazenado :", stored.isoformat())
print("em São Paulo:", stored.astimezone(sao_paulo).isoformat())
print("em Tóquio   :", stored.astimezone(tokyo).isoformat())

# replace(tzinfo=...) NÃO converte: apenas cola outro fuso.
wrong = stored.replace(tzinfo=sao_paulo)
print("replace  :", wrong.isoformat(), "(outro instante!)")
print("astimezone:", stored.astimezone(sao_paulo).isoformat())
