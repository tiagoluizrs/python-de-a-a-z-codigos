"""O hash de str, tuple, frozenset e frozendict é guardado no objeto."""
import time


def twice(label, value):
    start = time.perf_counter()
    hash(value)
    first = time.perf_counter() - start
    start = time.perf_counter()
    hash(value)
    second = time.perf_counter() - start
    print(f"{label:<28} 1ª chamada {first * 1e3:8.2f} ms"
          f"   2ª chamada {second * 1e6:8.2f} us")


twice("str de 10 milhões", "x" * 10_000_000)
twice("tuple de 1 milhão", tuple(range(1_000_000)))
twice("frozenset de 1 milhão", frozenset(range(1_000_000)))
twice("frozendict de 100 mil", frozendict({i: i for i in range(100_000)}))
