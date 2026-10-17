"""Exercício 1: o protocolo de iteração "à mão": iterável, iterador, iterador infinito e um iterador com ``peek``. (Sem geradores: classes com ``__next__``.)"""


class CountdownIterator:
    """O ITERADOR de ``Countdown``: ``CountdownIterator(start)`` produz ``start, start-1, ..., 0`` e depois levanta ``StopIteration``; ``__iter__`` devolve ele mesmo;
    continua levantando ``StopIteration`` se for chamado de novo depois de esgotado."""

    def __init__(self, start: int):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


class Countdown:
    """O ITERÁVEL: ``Countdown(start)`` (``start < 0``: ``ValueError("start negativo")``). ``__iter__`` devolve um ``CountdownIterator`` NOVO a cada chamada (por isso pode ser
    percorrido várias vezes); ``__len__`` é ``start + 1``; ``__contains__`` é ``0 <= n <= start`` para inteiros (qualquer outro valor: ``False``) sem percorrer."""

    def __init__(self, start: int):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __contains__(self, item) -> bool:
        raise NotImplementedError


class Fibonacci:
    """Um ITERADOR (de uma passada, ``iter(f) is f``) dos números de Fibonacci ``0, 1, 1, 2, 3, 5...``; ``Fibonacci(limit=None)``: com ``limit`` inteiro, produz no máximo
    ``limit`` números e depois ``StopIteration`` (``limit < 0``: ``ValueError("limit negativo")``); sem ``limit``, é infinito (use ``itertools.islice`` para cortar)."""

    def __init__(self, limit: int | None = None):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


class PeekableIterator:
    """Envolve QUALQUER iterável e permite espiar o próximo item. ``PeekableIterator(iterable)``:

    * ``__iter__`` devolve ele mesmo; ``__next__`` devolve o próximo item (primeiro os devolvidos por ``push_back``, do último para o primeiro, depois os do iterável);
    * ``peek(default=...)``: devolve o próximo item SEM consumi-lo; se acabou, devolve ``default`` se foi dado, senão levanta ``StopIteration``;
    * ``has_next()``: ``True`` se há próximo item (sem consumi-lo);
    * ``push_back(value)``: devolve ``value`` ao início (o próximo ``next``/``peek`` o verá primeiro; vários ``push_back`` formam uma pilha)."""

    def __init__(self, iterable):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError

    def peek(self, *default):
        raise NotImplementedError

    def has_next(self) -> bool:
        raise NotImplementedError

    def push_back(self, value) -> None:
        raise NotImplementedError
