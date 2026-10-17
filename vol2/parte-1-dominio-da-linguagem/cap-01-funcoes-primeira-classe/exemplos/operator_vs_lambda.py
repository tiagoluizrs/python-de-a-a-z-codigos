"""itemgetter, attrgetter, methodcaller e medição contra lambda."""
import timeit
from dataclasses import dataclass
from operator import attrgetter, itemgetter, methodcaller

rows = [("ana", 31, "SP"), ("bia", 25, "RJ"), ("caio", 31, "MG"),
        ("duda", 25, "SP")]
print(sorted(rows, key=itemgetter(1, 0)))
print(itemgetter(0, 2)(rows[0]), itemgetter("a")({"a": 1}))


@dataclass
class P:
    name: str
    age: int


ps = [P("x", 3), P("y", 1)]
print(sorted(ps, key=attrgetter("age")))
print(attrgetter("name", "age")(ps[0]))
print(methodcaller("split", ",")("a,b,c"))
print(list(map(methodcaller("upper"), ["a", "b"])))

big = [(i * 7919 % 10007, i) for i in range(10_000)]
dicts = [{"k": a, "v": b} for a, b in big]
objs = [P(str(a), b) for a, b in big]


def bench(label, fn):
    t = min(timeit.repeat(fn, number=30, repeat=5)) / 30
    print(f"{label:28s} {t * 1e6:8.1f} us")


bench("sorted key=lambda t: t[0]", lambda: sorted(big, key=lambda t: t[0]))
bench("sorted key=itemgetter(0)", lambda: sorted(big, key=itemgetter(0)))
bench("sorted dict lambda d['k']", lambda: sorted(dicts, key=lambda d: d["k"]))
bench("sorted dict itemgetter('k')", lambda: sorted(dicts, key=itemgetter("k")))
bench("sorted obj lambda o.age", lambda: sorted(objs, key=lambda o: o.age))
bench("sorted obj attrgetter", lambda: sorted(objs, key=attrgetter("age")))
bench("sorted lambda 2 chaves", lambda: sorted(big, key=lambda t: (t[0], t[1])))
bench("sorted itemgetter(0,1)", lambda: sorted(big, key=itemgetter(0, 1)))
