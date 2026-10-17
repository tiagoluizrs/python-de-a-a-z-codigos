"""Custo de chamada de função."""
import timeit


def empty():
    pass


def pos(a, b):
    return a


def kw(a=1, b=2):
    return a


def star(*args):
    return args


def kwstar(**kw):
    return kw


def inline():
    return 1

N = 2_000_000
cases = {
    "no call (pass)": "pass",
    "empty()": "empty()",
    "pos(1, 2)": "pos(1, 2)",
    "kw(a=1, b=2)": "kw(a=1, b=2)",
    "star(1, 2)": "star(1, 2)",
    "kwstar(a=1, b=2)": "kwstar(a=1, b=2)",
    "lambda call": "(lambda: 1)()",
    "len([])": "len(lst)",
}
for label, stmt in cases.items():
    t = min(timeit.repeat(stmt, globals={**globals(), "lst": []},
                          number=N, repeat=5))
    print(f"{label:<18}{t / N * 1e9:6.1f} ns")

# custo de uma chamada dentro de laço vs expressão inline
loop_call = "for i in range(1000): pos(i, 1)"
loop_inline = "for i in range(1000): i"
for label, stmt in (("loop com chamada", loop_call),
                    ("loop sem chamada", loop_inline)):
    t = min(timeit.repeat(stmt, globals=globals(), number=2000, repeat=5))
    print(f"{label:<18}{t / 2000 * 1e6:6.1f} us por 1000 iterações")
