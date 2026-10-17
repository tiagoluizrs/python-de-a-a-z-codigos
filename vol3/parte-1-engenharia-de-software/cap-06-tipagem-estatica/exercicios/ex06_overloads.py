"""Exercício 6: ``@overload`` (o tipo de retorno depende do argumento).

Implemente com sobrecargas tipadas:

* ``parse``: ``str`` -> ``int`` (``int(value)``), ``bytes`` -> ``str``
  (``value.decode()``), ``None`` -> ``None``;
* ``get[T](mapping, key)`` -> ``T | None`` e ``get[T, D](mapping, key, default:
  D)`` -> ``T | D`` para um ``Mapping[str, T]``: sem ``default``, ``None`` se
  faltar a chave; com ``default``, ele é devolvido.

A correção confere por ``reveal_type`` o tipo de cada chamada.
"""
from collections.abc import Mapping
from typing import overload


def parse(value):
    raise NotImplementedError


def get(mapping, key, default=None):
    raise NotImplementedError
