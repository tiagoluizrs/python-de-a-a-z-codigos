"""Horário de verão: horários inexistentes, ambíguos e fold.

Datas fixas e passadas (o Brasil aboliu o horário de verão em 2019):
 - 2018-11-04: à 00:00 os relógios de São Paulo pularam para 01:00.
 - 2019-02-17: à 00:00 voltaram para 23:00 do dia 16.
"""
import datetime as dt
from zoneinfo import ZoneInfo

sp = ZoneInfo("America/Sao_Paulo")
UTC = dt.UTC


def roundtrip_ok(moment: dt.datetime) -> bool:
    """False se o horário de parede não existe no fuso."""
    back = moment.astimezone(UTC).astimezone(moment.tzinfo)
    return back.replace(tzinfo=None) == moment.replace(tzinfo=None)


print("--- horário inexistente (salto) ---")
gap = dt.datetime(2018, 11, 4, 0, 30, tzinfo=sp)
print("digitado   :", gap, gap.utcoffset())
print("em UTC     :", gap.astimezone(UTC))
print("de volta   :", gap.astimezone(UTC).astimezone(sp))
print("existe?    :", roundtrip_ok(gap))

print("--- horário ambíguo (repetido) ---")
first = dt.datetime(2019, 2, 16, 23, 30, tzinfo=sp)
second = first.replace(fold=1)
for label, moment in (("fold=0", first), ("fold=1", second)):
    print(label, moment, moment.astimezone(UTC).time())

print("--- fold e igualdade ---")
print("first == second  :", first == second)
print("em UTC iguais    :", first.astimezone(UTC) == second.astimezone(UTC))
print("hash igual       :", hash(first) == hash(second))
print("tamanho do set   :", len({first, second}))
print("second - first   :", second - first)
print("UTC second-first :",
      second.astimezone(UTC) - first.astimezone(UTC))

print("--- aritmética de parede x absoluta ---")
ny = ZoneInfo("America/New_York")
start = dt.datetime(2024, 3, 9, 12, 0, tzinfo=ny)
wall = start + dt.timedelta(days=1)
absolute = (start.astimezone(UTC) + dt.timedelta(days=1)).astimezone(ny)
print("início          :", start)
print("parede  (+1 dia):", wall)
print("absoluta(+24 h) :", absolute)
print("wall - start    :", wall - start)
print("horas reais     :",
      (wall.astimezone(UTC) - start.astimezone(UTC)).total_seconds() / 3600)


def add_absolute(moment: dt.datetime, delta: dt.timedelta):
    """Soma tempo decorrido real (ida e volta por UTC)."""
    return (moment.astimezone(UTC) + delta).astimezone(moment.tzinfo)


print("add_absolute    :", add_absolute(start, dt.timedelta(days=1)))
