"""Quadros (frames), pilha de chamadas e o limite de recursão."""
import inspect
import sys
import timeit


def inner():
    frame = sys._getframe()                          # o quadro atual
    names = []
    while frame:
        names.append((frame.f_code.co_name, frame.f_lineno))
        frame = frame.f_back
    return names


def middle():
    return inner()


def outer():
    return middle()


stack = outer()
print([name for name, _ in stack][:4])

# Dentro do quadro: variáveis locais
def with_locals():
    a, b = 1, "x"
    return sys._getframe().f_locals


print(with_locals())

# inspect organiza o mesmo
def who_calls_me():
    return inspect.stack()[1].function


def caller():
    return who_calls_me()


print(caller())

# Limite de recursão: cada chamada Python ocupa um quadro
print("limite:", sys.getrecursionlimit())


def depth(n=0):
    try:
        return depth(n + 1)
    except RecursionError:
        return n


reached = depth()
print("profundidade alcançada:", reached)


# Mudar o limite não aumenta a pilha de C
def deep(n):
    return 0 if n == 0 else 1 + deep(n - 1)


old = sys.getrecursionlimit()
sys.setrecursionlimit(20_000)
print("deep(10_000) =", deep(10_000))
sys.setrecursionlimit(old)
try:
    deep(10_000)
except RecursionError as error:
    print("RecursionError:", error)

# Geradores: o quadro fica SUSPENSO entre os next()
def counter():
    n = 0
    while True:
        yield n
        n += 1


gen = counter()
next(gen)
next(gen)
print(gen.gi_frame.f_locals, gen.gi_frame.f_lineno, gen.gi_running)

# Recursão x laço (custo)
def sum_rec(n):
    return 0 if n == 0 else n + sum_rec(n - 1)


def sum_loop(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total


ns = dict(sum_rec=sum_rec, sum_loop=sum_loop)
for label, statement in [("recursão (n=500)", "sum_rec(500)"), ("laço (n=500)", "sum_loop(500)")]:
    seconds = min(timeit.repeat(statement, globals=ns, number=2000, repeat=5)) / 2000
    print(f"  {label:<20}{seconds * 1e6:8.1f} us")
