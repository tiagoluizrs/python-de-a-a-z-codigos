"""Exercício 4: recursão x iteração e o limite de recursão."""


def fact_recursive(n):
    """Fatorial recursivo. ``ValueError`` se ``n < 0``."""
    raise NotImplementedError


def fact_iterative(n):
    """Fatorial iterativo. ``ValueError`` se ``n < 0``."""
    raise NotImplementedError


def fib_iterative(n):
    """n-ésimo Fibonacci (fib(0)=0, fib(1)=1) em O(n), sem recursão."""
    raise NotImplementedError


def measured_depth():
    """Meça a profundidade atingida antes do ``RecursionError``.

    Escreva uma função recursiva que conta os níveis, provoque o erro,
    capture-o e devolva a profundidade alcançada. O valor deve ficar
    perto de ``sys.getrecursionlimit()`` (alguns níveis já estão em uso).
    """
    raise NotImplementedError
