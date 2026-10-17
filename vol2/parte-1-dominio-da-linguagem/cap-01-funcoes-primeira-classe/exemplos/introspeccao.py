"""inspect.signature, Parameter, bind, getsource."""
import inspect
from inspect import Parameter


def f(a, b=2, /, c=3, *args, d, e=5, **kw) -> str:
    """Exemplo."""
    return "ok"


sig = inspect.signature(f)
print(sig)
print(sig.return_annotation)
for p in sig.parameters.values():
    default = "-" if p.default is Parameter.empty else p.default
    print(f"{p.name:5s} {p.kind.name:22s} {default}")
print([k.name for k in type(sig.parameters["a"].kind)])

# bind: associa uma chamada a parâmetros
ba = sig.bind(1, 9, d=4)
print(ba.arguments)
ba.apply_defaults()
print(ba.arguments)
print(ba.args, ba.kwargs)
try:
    sig.bind(1)
except TypeError as e:
    print("TypeError:", e)
# "a" é somente posicional: o nome vai parar em **kw, sem erro
print(sig.bind(1, 2, 3, d=1, a=0).arguments)

# construir e alterar assinaturas
new = sig.replace(parameters=[p for p in sig.parameters.values()
                              if p.kind is not Parameter.VAR_KEYWORD])
print(new)

# getsource funciona para funções definidas em arquivo
print(inspect.getsource(f))
print(inspect.getsourcefile(f)[-16:], inspect.getsourcelines(f)[1])

# e não funciona para builtins, nem para código de exec/REPL
try:
    inspect.getsource(len)
except TypeError as e:
    print("TypeError:", e)
ns = {}
exec("def g():\n    return 1", ns)
try:
    inspect.getsource(ns["g"])
except OSError as e:
    print("OSError:", e)

# signature de builtins, classes e callables
for fn in (print, sorted, max, int):
    try:
        print(fn.__name__, inspect.signature(fn))
    except ValueError as e:
        print("ValueError:", e)


class K:
    def __init__(self, x, y=1):
        pass

    def __call__(self, z):
        pass


print(inspect.signature(K), inspect.signature(K(1)))
import functools
print(inspect.signature(functools.partial(f, 1, d=4)))
print(inspect.signature(functools.partial(f, 1, d=4)).bind(2))
