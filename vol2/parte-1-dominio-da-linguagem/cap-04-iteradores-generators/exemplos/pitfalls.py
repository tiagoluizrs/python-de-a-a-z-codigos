"""Armadilhas de geradores."""
import inspect
import traceback

# 1. gerador esgotado
gen = (n for n in range(3))
print(sum(gen), sum(gen))

# 2. dois consumidores dividem o mesmo gerador
gen = iter(range(6))
print(list(zip(gen, gen)))

# 3. closures tardias
gens = [(lambda: i) for i in range(3)]
print([g() for g in gens])
funcs = [(i for _ in range(1)) for i in range(3)]
print([next(f) for f in funcs])
# armadilha: iteravel externo avaliado cedo, interno nao
x = 10
late = (x + y for y in range(2))
x = 100
print(list(late))
base = [1, 2]
g = (n for n in base)
base = [9, 9]
print(list(g))
base2 = [1, 2]
g2 = (n for n in base2)
base2.append(3)
print(list(g2))

# 4. PEP 479
def broken():
    yield 1
    raise StopIteration("fim")


try:
    list(broken())
except RuntimeError as exc:
    print("RuntimeError:", exc, "| causa:", repr(exc.__cause__))


def inner_stop():
    it = iter([])
    yield next(it)


try:
    list(inner_stop())
except RuntimeError as exc:
    print("RuntimeError:", exc)


def safe():
    it = iter([])
    yield next(it, None)


print(list(safe()))

# 5. erro dentro do gerador e rastreamento
def parse(lines):
    for line in lines:
        yield int(line)


def total(lines):
    return sum(parse(lines))


try:
    total(["1", "2", "x"])
except ValueError:
    traceback.print_exc()

# 6. erro encerra o gerador
def erro():
    yield 1
    raise ValueError("falhou")
    yield 2


g = erro()
next(g)
try:
    next(g)
except ValueError:
    pass
print(inspect.getgeneratorstate(g), list(g))

# 7. gerador ja em execucao
def reentrant():
    yield next(g3)


g3 = reentrant()
try:
    next(g3)
except ValueError as exc:
    print("ValueError:", exc)

# 8. mutacao durante iteracao em gerador
data = [1, 2, 3, 4]
g = (n for n in data)
print(next(g))
data.remove(2)
print(list(g))

# 9. list(gen) duplicado
def counted():
    print("  gerando")
    yield 1


g = counted()
print(len(list(g)), len(list(g)))
print(bool((n for n in [])))       # gerador e sempre verdadeiro
try:
    len(n for n in [])
except TypeError as exc:
    print("TypeError:", exc)
