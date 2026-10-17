"""Depuração de decoradores: __wrapped__, unwrap e tracebacks."""
import functools
import inspect
import traceback


def deco_a(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def deco_b(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@deco_a
@deco_b
def target(x: int, *, scale: float = 1.0) -> float:
    """Multiplica x por scale."""
    return x * scale


# Descendo a pilha de embrulhos
layer = target
depth = 0
while hasattr(layer, "__wrapped__"):
    print("  " * depth + f"{layer.__qualname__}")
    layer = layer.__wrapped__
    depth += 1
print("  " * depth + layer.__qualname__)
print(inspect.unwrap(target) is layer)

# signature segue __wrapped__; follow_wrapped=False mostra o wrapper
print(inspect.signature(target))
print(inspect.signature(target, follow_wrapped=False))

# O que o functools.wraps NÃO resolve: o corpo do wrapper
print(inspect.getsource(target).splitlines()[0])
print(target.__code__.co_name, target.__code__.co_firstlineno)


# Traceback: o wrapper aparece na pilha
@deco_a
def explode():
    raise RuntimeError("boom")


try:
    explode()
except RuntimeError:
    for frame in traceback.extract_tb(
            __import__("sys").exc_info()[2]):
        print(frame.name, frame.lineno)


# Contornando o decorador em testes
print(target.__wrapped__.__wrapped__(3, scale=2.0))
