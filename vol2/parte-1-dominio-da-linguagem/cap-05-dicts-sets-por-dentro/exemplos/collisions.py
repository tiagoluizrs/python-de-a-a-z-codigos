"""Hash ruim: o dict degrada de O(1) para O(n) por busca."""
import time
import timeit


def make_class(name, hash_fn):
    class Key:
        eq_calls = 0

        def __init__(self, value):
            self.value = value

        def __hash__(self):
            return hash_fn(self.value)

        def __eq__(self, other):
            type(self).eq_calls += 1
            return self.value == other.value

    Key.__name__ = name
    return Key


Bad = make_class("Bad", lambda v: 1)          # hash constante
Good = make_class("Good", lambda v: hash(v))  # hash do valor

for n in (500, 1000, 2000, 4000):
    for cls in (Bad, Good):
        cls.eq_calls = 0
        keys = [cls(i) for i in range(n)]
        start = time.perf_counter()
        table = {key: 1 for key in keys}
        elapsed = time.perf_counter() - start
        print(f"{cls.__name__:<5} n={n:<5} __eq__ calls={cls.eq_calls:>8,}"
              f"  {elapsed * 1e3:8.1f} ms")

for cls in (Bad, Good):
    keys = [cls(i) for i in range(2000)]
    table = {key: 1 for key in keys}
    seconds = min(timeit.repeat(lambda: table[keys[-1]],
                                number=1000, repeat=3)) / 1000
    print(f"busca de uma chave em {cls.__name__}: {seconds * 1e9:,.0f} ns")
