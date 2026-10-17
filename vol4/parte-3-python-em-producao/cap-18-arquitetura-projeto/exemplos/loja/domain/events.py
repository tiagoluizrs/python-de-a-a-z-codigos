"""Eventos de domínio: fatos que já aconteceram (no passado, imutáveis)."""
from dataclasses import dataclass

from loja.domain.money import Money


@dataclass(frozen=True)
class OrderPlaced:
    order_id: str
    customer_id: str
    total: Money
