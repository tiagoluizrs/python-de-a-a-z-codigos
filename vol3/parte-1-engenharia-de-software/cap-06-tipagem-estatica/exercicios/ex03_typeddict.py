"""Exercício 3: ``TypedDict`` e validação de dados externos.

Defina:

* ``Address(TypedDict)``: ``street: str``, ``city: str``;
* ``User(TypedDict)``: ``name: str``, ``age: int``, ``address: Address`` e
  ``email: NotRequired[str]``;
* ``parse_user(data)``: recebe ``Mapping[str, object]`` (dados "de fora", sem
  garantia) e devolve ``User``. Valida em tempo de execução (``bool`` NÃO conta
  como ``int``) e levanta ``ValueError`` com o CAMINHO do campo: ``"name"``,
  ``"age"``, ``"address.city"``, ``"email"``. Chaves desconhecidas são ignoradas;
  ``email`` só entra no resultado se existir;
* ``summary(user)``: ``"Ana (30), Recife"`` (com `` <email>`` no fim se existir).

A correção roda ``mypy --strict`` e confere que construir um ``User`` sem
``name`` é um erro de tipo.
"""
from collections.abc import Mapping
from typing import NotRequired, TypedDict


def parse_user(data):
    raise NotImplementedError


def summary(user):
    raise NotImplementedError
