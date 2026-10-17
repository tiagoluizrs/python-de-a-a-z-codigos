"""Exercício 4: núcleo funcional (decide/evolve) para um carrinho dirigido por eventos."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CartState:
    items: tuple[tuple[str, int], ...] = ()          # ((sku, qty), ...) ordenado por sku
    closed: bool = False


@dataclass(frozen=True)
class AddItem:
    sku: str
    qty: int


@dataclass(frozen=True)
class RemoveItem:
    sku: str


@dataclass(frozen=True)
class CloseCart:
    pass


@dataclass(frozen=True)
class ItemAdded:
    sku: str
    qty: int


@dataclass(frozen=True)
class ItemRemoved:
    sku: str


@dataclass(frozen=True)
class CartClosed:
    pass


@dataclass(frozen=True)
class Rejected:
    reason: str


def decide(state: CartState, command) -> list:
    """PURA. (estado, comando) -> lista de eventos (nunca levanta por regra de negócio: rejeita com ``Rejected``).

    * ``AddItem`` com ``qty <= 0``: ``Rejected("quantidade inválida")``; carrinho fechado: ``Rejected("carrinho fechado")``;
      senão ``[ItemAdded(sku, qty)]``;
    * ``RemoveItem``: fechado -> ``Rejected("carrinho fechado")``; sku fora do carrinho -> ``Rejected("item não está no carrinho")``;
      senão ``[ItemRemoved(sku)]``;
    * ``CloseCart``: já fechado -> ``Rejected("carrinho fechado")``; vazio -> ``Rejected("carrinho vazio")``; senão ``[CartClosed()]``;
    * outro tipo de comando: ``TypeError``."""
    raise NotImplementedError


def evolve(state: CartState, event) -> CartState:
    """PURA. Aplica UM evento e devolve o novo estado (``Rejected`` não muda nada). ``ItemAdded`` soma a quantidade ao sku
    (criando-o se preciso) mantendo ``items`` ordenado por sku; ``ItemRemoved`` tira o sku; ``CartClosed`` marca ``closed``.
    Evento desconhecido: ``TypeError``."""
    raise NotImplementedError


def replay(events, initial: CartState = CartState()) -> CartState:
    """Reconstrói o estado aplicando ``events`` em ordem a partir de ``initial``."""
    raise NotImplementedError


def handle_all(commands, initial: CartState = CartState()) -> tuple[CartState, list]:
    """Executa os comandos em sequência (decide e depois aplica os eventos de cada um) e devolve ``(estado_final,
    todos_os_eventos)``. Os ``Rejected`` ENTRAM na lista de eventos (para auditoria), mas não mudam o estado."""
    raise NotImplementedError
