"""Exercício 2: ganhe um monte de métodos implementando só dois."""
from collections.abc import Sequence


class ArithSeq(Sequence):
    """Progressão aritmética ``start, start+step, ...`` com ``length`` termos.

    Implemente SÓ ``__init__``, ``__len__`` e ``__getitem__`` (e ``__repr__``).
    Todo o resto (``in``, ``index``, ``count``, ``reversed``, iteração) deve
    vir da classe base ``Sequence``.

    * ``ArithSeq(start, step, length)``;
    * índice inteiro (negativo funciona; fora do limite: ``IndexError``);
    * fatia devolve OUTRA ``ArithSeq`` (a fatia de uma progressão
      aritmética continua sendo uma progressão);
    * ``repr`` no formato ``ArithSeq(2, 3, 4)``.
    """

    def __init__(self, start, step, length):
        raise NotImplementedError
