"""Terceiro modulo: o que os dois compartilham."""
from dataclasses import dataclass, field


@dataclass
class Customer:
    name: str
    orders: list["Order"] = field(default_factory=list)


@dataclass
class Order:
    customer: Customer
