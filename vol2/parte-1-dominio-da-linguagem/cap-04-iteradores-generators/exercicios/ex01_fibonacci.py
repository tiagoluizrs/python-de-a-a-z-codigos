"""Exercício 1: Fibonacci como iterador (classe) e como gerador.

Implemente:

* ``FibIterator(limit=None)``: classe com ``__iter__`` e ``__next__``.
  Entrega 0, 1, 1, 2, 3, 5, ... e levanta ``StopIteration`` quando o
  próximo valor seria MAIOR que ``limit`` (se ``limit`` não for None).
* ``fib_gen(limit=None)``: a mesma sequência, como função geradora.

Dicas:
* O iterador é de uma passada: ``iter(obj) is obj``.
* ``limit`` negativo deve levantar ``ValueError`` na criação do
  ``FibIterator``. Em ``fib_gen`` o erro só aparece ao consumir (por quê?).

Exemplo: ``list(FibIterator(10)) == [0, 1, 1, 2, 3, 5, 8]``
"""


class FibIterator:
    def __init__(self, limit=None):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


def fib_gen(limit=None):
    raise NotImplementedError
