"""Exercício 1: um vetor 2D com aritmética completa."""
import math


class Vec:
    """Vetor 2D IMUTÁVEL.

    * ``Vec(x, y)`` e ``repr`` no formato ``Vec(1, 2)``;
    * ``+`` e ``-`` entre vetores;
    * ``*`` e ``/`` por escalar (``int`` ou ``float``); ``2 * v`` também funciona;
    * ``-v``, ``abs(v)`` (módulo), ``bool(v)`` (falso só para o vetor nulo);
    * ``v @ w`` é o produto escalar;
    * ``==`` e ``hash`` coerentes; ``Vec(1, 2) == (1, 2)`` é ``False``;
    * ``sum([v1, v2, v3])`` funciona (dica: ``__radd__`` com ``0``);
    * tipos não suportados devem fazer o Python levantar ``TypeError``
      (devolva ``NotImplemented``; NÃO levante você mesmo).
    """

    def __init__(self, x, y):
        raise NotImplementedError
