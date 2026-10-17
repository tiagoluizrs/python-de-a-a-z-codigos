"""Gabarito do exercício 4."""
from dataclasses import dataclass


@dataclass(frozen=True)
class CartState:
    items: tuple = ()
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


def decide(state, command):
    match command:
        case AddItem(sku, qty):
            if state.closed:
                return [Rejected("carrinho fechado")]
            if qty <= 0:
                return [Rejected("quantidade inválida")]
            return [ItemAdded(sku, qty)]
        case RemoveItem(sku):
            if state.closed:
                return [Rejected("carrinho fechado")]
            if sku not in dict(state.items):
                return [Rejected("item não está no carrinho")]
            return [ItemRemoved(sku)]
        case CloseCart():
            if state.closed:
                return [Rejected("carrinho fechado")]
            if not state.items:
                return [Rejected("carrinho vazio")]
            return [CartClosed()]
    raise TypeError(f"comando desconhecido: {command!r}")


def evolve(state, event):
    match event:
        case ItemAdded(sku, qty):
            items = dict(state.items)
            items[sku] = items.get(sku, 0) + qty
            return CartState(tuple(sorted(items.items())), state.closed)
        case ItemRemoved(sku):
            return CartState(tuple((s, q) for s, q in state.items if s != sku), state.closed)
        case CartClosed():
            return CartState(state.items, True)
        case Rejected():
            return state
    raise TypeError(f"evento desconhecido: {event!r}")


def replay(events, initial=CartState()):
    state = initial
    for event in events:
        state = evolve(state, event)
    return state


def handle_all(commands, initial=CartState()):
    state, history = initial, []
    for command in commands:
        events = decide(state, command)
        history += events
        state = replay(events, state)
    return state, history
