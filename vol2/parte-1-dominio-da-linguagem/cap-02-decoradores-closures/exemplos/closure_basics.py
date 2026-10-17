"""Closures: células, variáveis livres e estado privado."""
import dis


def make_counter(start=0):
    count = start

    def step():
        nonlocal count
        count += 1
        return count

    return step


counter = make_counter()
print(counter(), counter(), counter())

# Por dentro: o que a função interna carrega
print(counter.__code__.co_freevars)
print(make_counter.__code__.co_cellvars)
print(counter.__closure__)
print(counter.__closure__[0].cell_contents)

# Duas closures da mesma fábrica não compartilham estado
other = make_counter(100)
print(counter(), other())

print("--- bytecode da função interna")
dis.dis(counter)
print("--- bytecode da fábrica")
dis.dis(make_counter)


# Sem nonlocal, atribuir cria um local novo
def broken():
    total = 0

    def add(n):
        total += n   # UnboundLocalError
        return total

    return add


try:
    broken()(1)
except UnboundLocalError as exc:
    print(type(exc).__name__, exc)


# Closure que só LÊ não precisa de nonlocal
def make_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply


double = make_multiplier(2)
print(double(21), double.__closure__[0].cell_contents)


# Uma função sem variáveis livres não é closure
def plain():
    return 1


print(plain.__closure__)


# Duas funções internas compartilham a MESMA célula
def make_pair():
    items = []

    def push(x):
        items.append(x)

    def peek():
        return list(items)

    return push, peek


push, peek = make_pair()
push(1)
push(2)
print(peek(), push.__closure__[0] is peek.__closure__[0])


# A célula é "viva": a variável é capturada, não o valor
def make_late():
    x = 1

    def show():
        return x

    x = 2
    return show


print(make_late()())
