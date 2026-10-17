"""Tamanho em bytes, comparação, ordenação e hash de datas."""
import datetime as dt
import sys
import time
from zoneinfo import ZoneInfo

sp = ZoneInfo("America/Sao_Paulo")
samples = {
    "date": dt.date(2026, 10, 12),
    "time": dt.time(9, 30),
    "datetime naive": dt.datetime(2026, 10, 12, 9, 30),
    "datetime aware UTC": dt.datetime(2026, 10, 12, tzinfo=dt.UTC),
    "datetime aware zi": dt.datetime(2026, 10, 12, tzinfo=sp),
    "timedelta": dt.timedelta(days=1),
    "timezone(-3h)": dt.timezone(dt.timedelta(hours=-3)),
    "ZoneInfo": sp,
    "float (epoch)": time.time(),
    "int (epoch ns)": time.time_ns(),
    "str ISO": "2026-10-12T09:30:00+00:00",
}
for name, obj in samples.items():
    print(f"{name:20} {sys.getsizeof(obj):4} bytes")

# O aware ocupa o mesmo: o fuso é só uma referência (8 bytes dentro).
# Mas o fuso em si pode ser caro, e é compartilhado (cache).
print("ZoneInfo é singleton por chave:",
      ZoneInfo("America/Sao_Paulo") is sp)

print("--- comparar, ordenar, hash ---")
dates = [dt.date(2026, 3, 1), dt.date(2025, 12, 31), dt.date(2026, 1, 15)]
print(sorted(dates))
print(max(dates), min(dates))
print(dates[0] in {dt.date(2026, 3, 1)})
print({dt.date(2026, 1, 15): "feriado"}[dt.date(2026, 1, 15)])

print("date == datetime:", dt.date(2026, 1, 1) == dt.datetime(2026, 1, 1))
try:
    dt.date(2026, 1, 1) < dt.datetime(2026, 1, 1)
except TypeError as error:
    print("date < datetime:", error)

# Aware ordena pelo instante, mesmo em fusos diferentes.
a = dt.datetime(2026, 1, 1, 12, tzinfo=dt.UTC)
b = dt.datetime(2026, 1, 1, 10, tzinfo=sp)      # 13:00 UTC
print(a < b, sorted([b, a]) == [a, b])
print("hash(a) == hash(a em SP):",
      hash(a) == hash(a.astimezone(sp)))

# Datas são hashable (imutáveis): servem de chave de dict e membro de set.
events = {}
events.setdefault(dt.date(2026, 10, 12), []).append("reunião")
print(events)
