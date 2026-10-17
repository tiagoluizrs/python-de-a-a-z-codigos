"""Estilo funcional: composição, funções puras e o custo de map/filter/reduce."""
import operator
import timeit
from functools import reduce


# Funções puras: mesma entrada, mesma saída, sem efeito colateral
def price_with_tax(price, rate):
    return round(price * (1 + rate), 2)


print(price_with_tax(100, 0.1), price_with_tax(100, 0.1))


# Composição
def compose(*funcs):
    """compose(f, g, h)(x) == f(g(h(x)))"""
    def composed(value):
        for func in reversed(funcs):
            value = func(value)
        return value
    return composed


def pipe(value, *funcs):
    """pipe(x, f, g, h) == h(g(f(x)))"""
    for func in funcs:
        value = func(value)
    return value


clean = compose(str.title, str.strip)
print(clean("  maria da silva "), pipe("  maria da silva ", str.strip, str.title))
print(pipe(range(10), lambda xs: filter(lambda n: n % 2, xs), lambda xs: map(lambda n: n * n, xs), sum))

# reduce: o que ele faz, passo a passo
steps = []
reduce(lambda acc, x: steps.append((acc, x)) or acc + x, [1, 2, 3, 4])
print(steps)

# reduce vs alternativas
numbers = list(range(1, 6))
print(reduce(operator.mul, numbers), reduce(operator.add, numbers, 100), sum(numbers))

# any/all: curto-circuito sobre geradores
print(any(n > 3 for n in numbers), all(n > 0 for n in numbers))


# Currying simples
def curry2(func):
    return lambda a: lambda b: func(a, b)


add = curry2(operator.add)
print(add(1)(2), list(map(add(10), [1, 2, 3])))

# Dados imutáveis + funções = sem estado compartilhado
def add_item(cart, item):
    return (*cart, item)                                    # devolve uma NOVA tupla


cart0 = ()
cart1 = add_item(cart0, "a")
cart2 = add_item(cart1, "b")
print(cart0, cart1, cart2)

# Custo: map/filter/reduce x compreensões x laço (1000 itens)
L = list(range(1000))
ns = dict(L=L, operator=operator, reduce=reduce)
cases = [
    ("sum(L)", "sum(L)"),
    ("reduce(operator.add)", "reduce(operator.add, L)"),
    ("reduce(lambda)", "reduce(lambda a, b: a + b, L)"),
    ("map(lambda)", "list(map(lambda x: x * 2, L))"),
    ("compreensão", "[x * 2 for x in L]"),
    ("map(operator.neg)", "list(map(operator.neg, L))"),
    ("filter(lambda)", "list(filter(lambda x: x % 2, L))"),
    ("compreensão c/ if", "[x for x in L if x % 2]"),
]
print("1000 itens (us):")
for label, statement in cases:
    seconds = min(timeit.repeat(statement, globals=ns, number=2000, repeat=5)) / 2000
    print(f"  {label:<22}{seconds * 1e6:7.1f}")
