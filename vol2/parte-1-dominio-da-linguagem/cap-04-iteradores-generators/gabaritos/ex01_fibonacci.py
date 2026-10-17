"""Gabarito 1: Fibonacci como classe iteradora e como gerador."""


class FibIterator:
    def __init__(self, limit=None):
        if limit is not None and limit < 0:
            raise ValueError("limit must be >= 0")
        self.limit = limit
        # estado explícito: o par (atual, próximo)
        self._a, self._b = 0, 1

    def __iter__(self):
        # iterador é iterável de si mesmo: uma única passada
        return self

    def __next__(self):
        if self.limit is not None and self._a > self.limit:
            raise StopIteration
        value = self._a
        self._a, self._b = self._b, self._a + self._b
        return value


def fib_gen(limit=None):
    # No gerador, o estado vive nas variáveis locais, e o corpo da
    # função só roda no primeiro next(): por isso uma validação feita
    # aqui só dispararia ao consumir, não na chamada.
    a, b = 0, 1
    while limit is None or a <= limit:
        yield a
        a, b = b, a + b
