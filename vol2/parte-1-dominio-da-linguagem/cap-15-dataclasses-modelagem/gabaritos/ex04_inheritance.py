"""Gabarito do exercício 4."""
from dataclasses import dataclass


@dataclass
class Entity:
    id: int
    created: str = "hoje"


@dataclass(kw_only=True)
class Customer(Entity):
    name: str                                # obrigatório, mesmo após um campo com padrão
    vip: bool = False
