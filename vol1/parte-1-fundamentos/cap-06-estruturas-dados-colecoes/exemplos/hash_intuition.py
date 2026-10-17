"""Intuição da tabela de hash: hash, colisão e custo (detalhes: Cap. 5 do Volume 2)."""
import timeit


class GoodKey:
    def __init__(self, n):
        self.n = n

    def __eq__(self, other):
        return self.n == other.n

    def __hash__(self):
        return hash(self.n)


class BadKey(GoodKey):
    def __hash__(self):
        return 42                      # todos colidem


for n in (100, 400, 1600):
    good = {GoodKey(i): i for i in range(n)}
    bad = {BadKey(i): i for i in range(n)}
    probe_good, probe_bad = GoodKey(n - 1), BadKey(n - 1)
    t_good = timeit.timeit(lambda: probe_good in good, number=2000) / 2000
    t_bad = timeit.timeit(lambda: probe_bad in bad, number=2000) / 2000
    print(f"n={n:>5}: hash bom {t_good * 1e9:7.0f} ns | "
          f"hash constante {t_bad * 1e9:9.0f} ns")

# Regra: se a == b, então hash(a) == hash(b)
print(hash("python") == hash("py" + "thon"), hash(1) == hash(1.0))
print(hash((1, 2)) == hash((1, 2)), hash(-1), hash(-2))
