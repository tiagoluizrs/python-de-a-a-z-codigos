"""Objetos naive x aware e o TypeError ao misturá-los."""
import datetime as dt

naive = dt.datetime(2026, 10, 12, 9, 0)
aware = dt.datetime(2026, 10, 12, 9, 0, tzinfo=dt.UTC)

print(repr(naive))
print(repr(aware))
print("utcoffset naive:", naive.utcoffset())
print("utcoffset aware:", aware.utcoffset())
print("tzname aware:", aware.tzname())

# Igualdade nunca falha, mas é sempre False entre naive e aware.
print("naive == aware:", naive == aware)

for label, operation in [
    ("naive < aware", lambda: naive < aware),
    ("naive - aware", lambda: naive - aware),
]:
    try:
        operation()
    except TypeError as error:
        print(f"{label}: TypeError: {error}")

# Como saber se um datetime é aware (regra da documentação):
def is_aware(value: dt.datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None

print(is_aware(naive), is_aware(aware))

# O mesmo instante em dois fusos: iguais, hash igual.
sao_paulo = dt.timezone(dt.timedelta(hours=-3))
local = aware.astimezone(sao_paulo)
print(local, "|", aware)
print("mesmo instante:", local == aware, hash(local) == hash(aware))

# astimezone em um naive ASSUME o fuso do sistema (cuidado!).
print("naive.astimezone():", naive.astimezone())
