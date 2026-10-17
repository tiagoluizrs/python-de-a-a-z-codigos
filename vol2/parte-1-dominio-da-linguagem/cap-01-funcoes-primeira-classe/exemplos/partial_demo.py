"""functools.partial, Placeholder (3.14), partialmethod, reduce."""
import functools
import operator
import timeit


def power(base, exponent):
    return base ** exponent


square = functools.partial(power, exponent=2)
print(square(7), square)
print(square.func is power, square.args, square.keywords)

pb = functools.partial(power, 2)       # fixa o primeiro posicional
print(pb(10))
# Placeholder (novo no 3.14): fixar um argumento do meio/fim
from functools import Placeholder as _
p2 = functools.partial(power, _, 2)
print(p2(9))
print(p2)

print(functools.partial(int, base=2)("1010"))


class Cell:
    def __init__(self):
        self.state = "off"

    def _set(self, value):
        self.state = value
        return self

    turn_on = functools.partialmethod(_set, "on")
    turn_off = functools.partialmethod(_set, "off")


c = Cell()
print(c.turn_on().state, c.turn_off().state)

print(functools.reduce(operator.add, [1, 2, 3, 4]))
print(functools.reduce(operator.mul, range(1, 6), 1))
print(functools.reduce(lambda a, b: a + b, [], 0))
try:
    functools.reduce(operator.add, [])
except TypeError as e:
    print("TypeError:", e)
print(functools.reduce(operator.add, [[1], [2], [3]], initial=[]))


def f(x):
    return power(x, 2)


g = lambda x: power(x, 2)
h = functools.partial(power, exponent=2)
k = functools.partial(power, _, 2)
pp = functools.partial(power, 3)
N = 1_000_000
cases = [("def f(3)", "f(3)"), ("lambda g(3)", "g(3)"),
         ("partial kw h(3)", "h(3)"),
         ("partial pos pp(2)", "pp(2)"), ("partial _ k(3)", "k(3)"),
         ("direta power(3, 2)", "power(3, 2)")]
for name, stmt in cases:
    t = min(timeit.repeat(stmt, globals=globals(), number=N,
                          repeat=5)) / N
    print(f"{name:20s} {t * 1e9:6.1f} ns")
