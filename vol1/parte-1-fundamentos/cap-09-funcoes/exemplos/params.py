"""Parâmetros: posicionais, nomeados, padrão, *args, **kwargs, / e *."""


def connect(host, port=5432, *, timeout=10.0):
    return f"{host}:{port} (timeout={timeout})"


def only_pos(a, b, /, c):
    return (a, b, c)


def collect(first, *rest, **options):
    return first, rest, options


print(connect("db"))
print(connect("db", 3306, timeout=2))
print(only_pos(1, 2, c=3))
try:
    only_pos(a=1, b=2, c=3)
except TypeError as exc:
    print("TypeError:", exc)
try:
    connect("db", 1, 2)
except TypeError as exc:
    print("TypeError:", exc)
try:
    connect("db", host="x")
except TypeError as exc:
    print("TypeError:", exc)
print(collect(1, 2, 3, x=4))

args = ["db", 3306]
kwargs = {"timeout": 1.5}
print(connect(*args, **kwargs))
print(collect(*"ab", **{"k": 1}, z=2))

# vários retornos = uma tupla
def min_max(values):
    return min(values), max(values)

low, high = min_max([3, 1, 4])
print(low, high, min_max([3, 1, 4]))


def nothing():
    pass

print(nothing())
