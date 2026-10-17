"""Gabarito do exercício 1."""
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Product:
    sku: str
    name: str
    price: Decimal
    tags: list[str] = field(default_factory=list)
    slug: str = field(init=False, repr=False)

    def __post_init__(self):
        self.sku = self.sku.strip().upper()
        if not self.name.strip():
            raise ValueError("nome vazio")
        if self.price < 0:
            raise ValueError("preço negativo")
        self.slug = "-".join(self.name.lower().split())
