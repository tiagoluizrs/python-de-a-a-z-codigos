"""Funções são objetos: atribuir, guardar, passar, devolver, atributos."""
import functools
import sys


def square(x: int, y: int = 2, *rest, flag=False) -> int:
    """Eleva x ao quadrado."""
    return x * x


# 1. funções são valores comuns
alias = square
table = {"sq": square, "len": len}
print(alias is square, table["sq"](4))
print(type(square), type(len), type(alias).__mro__)

# 2. identidade
print(square.__name__, square.__qualname__, square.__module__)
print(square.__doc__)


class Box:
    def method(self):
        def inner():
            pass
        return inner


print(Box.method.__qualname__)
print(Box().method().__qualname__)

# 3. atributos próprios em __dict__
print(square.__dict__)
square.calls = 0
square.calls += 1
print(square.__dict__)

# 4. defaults e anotações
print(square.__defaults__, square.__kwdefaults__)
print(square.__annotations__)

# 5. __code__
code = square.__code__
print(code.co_name, code.co_argcount, code.co_kwonlyargcount)
print(code.co_varnames, code.co_flags & 0x04 != 0)
print(code.co_consts, code.co_names, code.co_filename[-17:])
print(code.co_firstlineno, len(code.co_code), "bytes de bytecode")
print(sys.getsizeof(square), sys.getsizeof(code))


# 6. __wrapped__
def deco(fn):
    @functools.wraps(fn)
    def wrapper(*a, **k):
        return fn(*a, **k)
    return wrapper


wrapped = deco(square)
print(wrapped.__name__, wrapped.__wrapped__ is square)

# 7. troca de __defaults__ em tempo de execução
square.__defaults__ = (10,)
print(square.__defaults__)
