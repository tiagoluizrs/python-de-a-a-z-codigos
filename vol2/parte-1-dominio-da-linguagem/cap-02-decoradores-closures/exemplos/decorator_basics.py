"""O que o @ realmente faz, e o que acontece sem wraps."""
import dis
import functools
import inspect


def shout(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper


@shout
def greet(name: str) -> str:
    """Devolve uma saudação."""
    return f"hello, {name}"


print(greet("ana"))


# Equivalência: @shout é só açúcar para uma atribuição
def greet2(name: str) -> str:
    """Devolve uma saudação."""
    return f"hello, {name}"


greet2 = shout(greet2)
print(greet2("bia"))

# Sem functools.wraps a identidade da função se perde
print(greet.__name__, greet.__doc__)
print(inspect.signature(greet))
print(greet.__closure__[0].cell_contents)


# Com wraps
def shout_ok(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper


@shout_ok
def greet3(name: str) -> str:
    """Devolve uma saudação."""
    return f"hello, {name}"


print(greet3.__name__, greet3.__doc__)
print(inspect.signature(greet3))
print(greet3.__wrapped__)
print(inspect.unwrap(greet3) is greet3.__wrapped__)
print(sorted(greet3.__dict__))


# O bytecode de uma função decorada
def build():
    @shout_ok
    def f(x):
        return x
    return f


dis.dis(build)
