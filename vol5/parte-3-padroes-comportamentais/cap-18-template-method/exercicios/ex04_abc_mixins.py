"""Exercício 4: o Template Method das ABCs de ``collections.abc``: implemente os métodos ABSTRATOS e ganhe os outros de graça (os "mixins")."""
from collections.abc import Mapping, MutableSet, Sequence


class Countdown(Sequence):
    """``Countdown(start)``: a sequência ``start, start-1, ..., 0``. Implemente SÓ ``__len__`` (``start + 1``) e ``__getitem__`` (índice inteiro, inclusive negativo; ``slice``
    devolvendo uma ``list``; índice fora: ``IndexError``). Com isso ``in``, ``iter``, ``reversed``, ``index`` e ``count`` já funcionam (da ``Sequence``). ``start < 0``:
    ``ValueError("start negativo")``."""

    def __init__(self, start: int):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, index):
        raise NotImplementedError


class CaseInsensitiveMap(Mapping):
    """Um ``Mapping`` somente leitura cujas chaves de TEXTO são comparadas sem diferenciar maiúsculas de minúsculas. ``CaseInsensitiveMap(data)`` copia o ``dict`` ``data``
    (chaves que são ``str``; duas chaves iguais sem considerar a caixa: ``ValueError(f"chave duplicada: {chave}")``). Implemente SÓ ``__getitem__``, ``__iter__`` e ``__len__``:
    ``__getitem__("ABC")`` acha ``"abc"``; ``__iter__`` produz as chaves ORIGINAIS na ordem de inserção; chave que não é ``str`` na consulta: ``KeyError`` normal.
    Com isso ``keys``, ``items``, ``values``, ``get``, ``in`` e ``==`` já funcionam (da ``Mapping``)."""

    def __init__(self, data: dict):
        raise NotImplementedError

    def __getitem__(self, key):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class OrderedSet(MutableSet):
    """Um conjunto que preserva a ORDEM de inserção. Implemente SÓ ``__contains__``, ``__iter__``, ``__len__``, ``add`` e ``discard`` (use um ``dict`` por baixo): a
    ``MutableSet`` oferece ``|``, ``&``, ``-``, ``^``, ``<=``, ``isdisjoint``, ``remove``, ``pop``, ``clear``, ``|=`` etc. ``OrderedSet(items=())`` aceita qualquer iterável.
    ``repr``: ``OrderedSet([1, 2, 3])``. Dica: a ``MutableSet`` cria o resultado das operações binárias com ``self._from_iterable(it)`` (um ``classmethod``: devolva
    ``cls(it)``)."""

    def __init__(self, items=()):
        raise NotImplementedError

    def __contains__(self, item) -> bool:
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def add(self, item) -> None:
        raise NotImplementedError

    def discard(self, item) -> None:
        raise NotImplementedError

    @classmethod
    def _from_iterable(cls, it):
        raise NotImplementedError

    def __repr__(self) -> str:
        raise NotImplementedError
