"""doctest: exemplos na documentação que também são testes."""
import doctest
import sys
import types


def good(x):
    """Dobra.

    >>> good(2)
    4
    >>> good("ab")
    'abab'
    """
    return x * 2


def bad(x):
    """Um exemplo desatualizado.

    >>> bad(2)
    5
    """
    return x * 2


def fuzzy(items):
    """Saídas variáveis: ELLIPSIS e NORMALIZE_WHITESPACE.

    >>> fuzzy([1, 2, 3])  # doctest: +ELLIPSIS
    <list object at 0x...>
    >>> print("a   b\\n   c")  # doctest: +NORMALIZE_WHITESPACE
    a b c
    """
    return items


module = types.ModuleType("demo")
for fn in (good, bad, fuzzy):
    setattr(module, fn.__name__, fn)
    fn.__module__ = "demo"
sys.modules["demo"] = module
module.__dict__["__doc__"] = ""
finder = doctest.DocTestFinder()
runner = doctest.DocTestRunner(optionflags=0)
for fn in (good, bad):
    for test in finder.find(fn, fn.__name__, globs={fn.__name__: fn}):
        runner.run(test, out=lambda text: None)
print(f"doctest: {runner.tries} exemplos, {runner.failures} falhas")
print("falha típica (exemplo desatualizado): esperado 5, obtido", bad(2))

# Armadilhas
print("float:", 0.1 + 0.2, "<- um exemplo com esse resultado precisa mostrar o repr completo (0.30000000000000004)")
print("dict de ordem de inserção é estável desde o 3.7, mas set de textos NÃO é (hash aleatorizado):")
print("  ", [sorted({"b", "a", "c"})][0], "(use sorted para um exemplo estável)")
