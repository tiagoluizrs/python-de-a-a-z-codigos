"""Exercício 5: um mapeamento imutável com collections.abc.Mapping."""
from collections.abc import Mapping


class FrozenMap(Mapping):
    """Mapeamento imutável e hasheável.

    Implemente SÓ ``__init__``, ``__getitem__``, ``__iter__``,
    ``__len__`` e ``__hash__``; ``get``, ``keys``, ``items``, ``values``,
    ``in`` e ``==`` vêm de graça da classe base ``Mapping``.

    * ``FrozenMap(pairs_or_mapping)`` copia os dados (não guarde o dict
      do chamador);
    * a iteração segue a ordem de inserção;
    * ``hash`` não depende da ordem (use ``frozenset`` dos itens);
    * não deve existir ``__setitem__``.
    """

    def __init__(self, data=()):
        raise NotImplementedError
