"""Funcao geradora: estado preservado, gi_frame, dis."""
import dis
import inspect


def count_to(limit):
    print("  [inicio]")
    n = 1
    while n <= limit:
        print(f"  [vai entregar {n}]")
        yield n
        print(f"  [retomou apos {n}]")
        n += 1
    print("  [fim]")


gen = count_to(2)
print(type(gen).__name__, inspect.getgeneratorstate(gen))
print("next ->", next(gen))
print(inspect.getgeneratorstate(gen), gen.gi_frame.f_locals)
print("next ->", next(gen))
print(gen.gi_frame.f_lineno)
try:
    next(gen)
except StopIteration:
    print("StopIteration")
print(inspect.getgeneratorstate(gen), gen.gi_frame)


def probe():
    yield gen2.gi_running
    yield inspect.getgeneratorstate(gen2)


gen2 = probe()
print(list(gen2))

print(count_to.__code__.co_flags & inspect.CO_GENERATOR != 0)
print(inspect.isgeneratorfunction(count_to), inspect.isgenerator(gen))
dis.dis(count_to)
