"""Operadores sobrecarregados na biblioteca padrão."""
import datetime as dt
from collections import Counter
from fractions import Fraction
from pathlib import PurePosixPath

print(PurePosixPath("/srv") / "app" / "log.txt")        # __truediv__
print(dt.datetime(2026, 10, 12) - dt.datetime(2026, 10, 1))   # datetime - datetime
print(dt.date(2026, 10, 12) + dt.timedelta(days=30))
print({1, 2} | {2, 3}, {1, 2} & {2, 3}, {1, 2} - {2})        # __or__, __and__, __sub__
print(Counter("aab") + Counter("bcc"))                        # soma de contagens
print(Fraction(1, 3) + Fraction(1, 6), Fraction(1, 3) * 3)
print([1, 2] * 2, "ab" * 3, (1,) + (2,))                       # repetição e concatenação
print("%s tem %d anos" % ("Ana", 30))                           # str.__mod__
print(dt.timedelta(hours=1) * 3, dt.timedelta(days=1) / dt.timedelta(hours=6))
try:
    dt.datetime(2026, 1, 1) + dt.datetime(2026, 1, 2)
except TypeError as error:
    print("TypeError:", error)
