"""A armadilha do valor padrão mutável e suas correções."""


def add_bad(item, bucket=[]):
    bucket.append(item)
    return bucket


print(add_bad(1), add_bad(2))
print(add_bad.__defaults__)
print(add_bad(3) is add_bad.__defaults__[0])


def add_none(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket


print(add_none(1), add_none(2))

MISSING = sentinel("MISSING")


def first(items, default=MISSING):
    for item in items:
        return item
    if default is MISSING:
        raise ValueError("empty and no default")
    return default


print(first([], None), first([7]), MISSING, repr(MISSING))
try:
    first([])
except ValueError as exc:
    print("ValueError:", exc)

# o padrão é avaliado UMA vez, na execução do def
import time


def stamp(t=time.perf_counter_ns()):
    return t

print(stamp() == stamp())
