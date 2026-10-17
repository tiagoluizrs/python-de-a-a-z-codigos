"""Exercício 4: ``take`` e ``windowed``.

* ``take(n, iterable)``: lista com os ``n`` primeiros itens (menos, se
  o iterável for curto). Não pode consumir mais que ``n`` itens de um
  iterador (teste: depois de ``take(2, it)``, ``next(it)`` é o 3º item).
* ``windowed(iterable, size)``: gerador de tuplas com ``size`` itens
  consecutivos, deslizando de um em um. Use ``collections.deque`` com
  ``maxlen``. Iterável menor que ``size`` não entrega nada.
  ``size < 1`` levanta ``ValueError`` ao consumir.
* ``moving_average(values, size)``: gerador com a média de cada janela.

Exemplo: ``list(windowed("abcd", 3)) == [("a","b","c"), ("b","c","d")]``
"""


def take(n, iterable):
    raise NotImplementedError


def windowed(iterable, size):
    raise NotImplementedError


def moving_average(values, size):
    raise NotImplementedError
