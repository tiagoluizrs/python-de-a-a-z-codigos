"""Exercício 2: uma classe hasheável escrita do jeito certo."""


class Point:
    """Ponto imutável (x, y) que funciona como chave de dict.

    Requisitos:

    * ``Point(1, 2) == Point(1.0, 2.0)`` e os hashes também são iguais;
    * ``==`` com outro tipo devolve ``NotImplemented`` (então
      ``Point(1, 2) == (1, 2)`` é ``False``);
    * depois de criado, atribuir a ``x`` ou ``y`` levanta
      ``AttributeError`` (a chave não pode mudar);
    * use ``__slots__``;
    * ``repr`` no formato ``Point(1, 2)``.
    """

    def __init__(self, x, y):
        raise NotImplementedError
