"""Exercício 4: a ORDEM dos decoradores: ``@a @b def f`` é ``f = a(b(f))``, e o de cima é o mais EXTERNO."""
import functools


def stack(fn, *decorators):
    """Aplica ``decorators`` a ``fn`` como se estivessem escritos, na ordem dada, de CIMA para BAIXO sobre ``fn``:
    ``stack(f, a, b)`` equivale a ``@a @b def f`` (``a(b(f))``). Sem decoradores, devolve ``fn``."""
    raise NotImplementedError


def labeled(name: str, log: list):
    """Decorador (use ``@labeled("A", log)``) que, a cada chamada, acrescenta ``f"entra {name}"`` a ``log`` antes de chamar a função, e ``f"sai {name}"``
    depois (mesmo se ela levantar uma exceção). Preserva a identidade da função (``functools.wraps``)."""
    raise NotImplementedError


def explain_order(names: list[str]) -> list[str]:
    """Monta ``@labeled(n1) @labeled(n2) ... def f``, na ordem de ``names``, onde ``f`` acrescenta ``"f"`` ao log; chama a função UMA vez e devolve o log.
    ``["A", "B"]`` -> ``["entra A", "entra B", "f", "sai B", "sai A"]``. Lista vazia: ``["f"]``."""
    raise NotImplementedError


def unwrap_chain(fn) -> list:
    """Segue ``__wrapped__`` do mais externo ao mais interno e devolve a lista de TODAS as funções da cadeia, a começar por ``fn`` e terminando na função
    original (a que não tem ``__wrapped__``). Função sem ``__wrapped__``: lista com ela mesma."""
    raise NotImplementedError


def count_layers(fn) -> int:
    """Quantos decoradores com ``functools.wraps`` embrulham ``fn``: ``len(unwrap_chain(fn)) - 1``."""
    raise NotImplementedError
