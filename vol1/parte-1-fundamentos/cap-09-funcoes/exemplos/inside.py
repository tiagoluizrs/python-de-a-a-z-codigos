"""O que uma função é por dentro."""
import dis
import inspect


def area(width: float, height: float = 1.0, *extra, flag=False) -> float:
    """Área de um retângulo."""
    return width * height


print(type(area), area.__name__, area.__qualname__)
print(area.__defaults__, area.__kwdefaults__)
print(area.__annotations__)
print(area.__doc__)
code = area.__code__
print(code.co_varnames, code.co_argcount, code.co_kwonlyargcount)
print(code.co_flags & inspect.CO_VARARGS != 0)
print(inspect.signature(area))
for p in inspect.signature(area).parameters.values():
    print(p.name, p.kind.name, p.default)
print(sorted(set(dir(area)) - set(dir(object)))[:12])
area.version = 2
print(area.__dict__)


def caller():
    return area(2, 3)


dis.dis(caller)
print(len(code.co_code))
help(area)
