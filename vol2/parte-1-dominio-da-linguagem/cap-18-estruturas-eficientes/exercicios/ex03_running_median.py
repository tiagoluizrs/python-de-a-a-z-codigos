"""Exercício 3: mediana em fluxo com dois heaps."""


class RunningMedian:
    """Mediana dos valores vistos, com ``add`` em O(log n) e ``median`` em O(1).

    Técnica: um max-heap com a metade menor e um min-heap com a metade maior
    (em ``heapq`` de min-heap, guarde a metade menor com sinal trocado). Os
    tamanhos nunca diferem em mais de 1.

    * ``add(value)``;
    * ``median()``: o valor central (``float``) ou a média dos dois centrais;
      sem valores, levanta ``ValueError``.
    """

    def __init__(self):
        raise NotImplementedError
