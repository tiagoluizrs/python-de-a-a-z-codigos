"""Funções internas: custo de criação, bytecode e limites do lambda."""
import dis
import timeit


def helper(x):
    return x + 1


def with_global(x):
    return helper(x)


def with_nested(x):
    def inner(y):
        return y + 1
    return inner(x)


def with_closure(x):
    def inner():
        return x + 1
    return inner()


dis.dis(with_nested)
print("---")
N = 1_000_000
for name, stmt in [("global helper", "with_global(1)"),
                   ("nested sem captura", "with_nested(1)"),
                   ("nested com closure", "with_closure(1)")]:
    t = min(timeit.repeat(stmt, globals=globals(), number=N,
                          repeat=5)) / N
    print(f"{name:20s} {t * 1e9:6.1f} ns")

# cada execução do def cria um objeto novo
def make():
    def inner():
        pass
    return inner


a, b = make(), make()
print(a is b, a.__code__ is b.__code__)

# limites do lambda
try:
    eval("lambda x: (y = x)")
except SyntaxError as e:
    print("SyntaxError:", e.msg)
f = lambda x: x
print(f.__name__, f.__qualname__, f.__doc__)
try:
    (lambda x: 1 / x)(0)
except ZeroDivisionError:
    import traceback
    print(traceback.format_exc().splitlines()[-4].strip())

# armadilha clássica: lambda em laço captura a VARIÁVEL
fs = [lambda: i for i in range(3)]
print([g() for g in fs])
fs = [lambda i=i: i for i in range(3)]
print([g() for g in fs])
import functools
fs = [functools.partial(int.__add__, i) for i in range(3)]
print([g(10) for g in fs])
