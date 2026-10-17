"""Exercício 4: um tipo imutável com __new__ (subclasse de tuple)."""


class Point(tuple):
    """Ponto 2D imutável, que É uma tupla ``(x, y)``.

    * ``Point(1, 2)``; ``p.x`` e ``p.y`` por atributo (use ``property`` com
      ``operator.itemgetter``);
    * é uma tupla: ``p == (1, 2)``, ``x, y = p``, ``len(p) == 2``, ``hash``;
    * ``__slots__ = ()`` (sem ``__dict__``: nenhum atributo novo);
    * ``repr`` no formato ``Point(x=1, y=2)``;
    * ``p.moved(dx, dy)`` devolve um NOVO ``Point``;
    * coordenadas que não sejam números (``int``/``float``) levantam
      ``TypeError`` na criação.
    """

    def __new__(cls, x, y):
        raise NotImplementedError
