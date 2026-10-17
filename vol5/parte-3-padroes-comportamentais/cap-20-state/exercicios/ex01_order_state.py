"""Exercício 1: o State clássico: um pedido cujo comportamento depende do estado, uma classe por estado."""


class InvalidTransition(Exception):
    pass


class State:
    """A base: ``name`` (texto, definido em cada estado) e as quatro operações ``pay``, ``ship``, ``deliver`` e ``cancel``, que por padrão NEGAM:
    ``InvalidTransition(f"{evento} não permitido em {self.name}")``. Cada operação recebe o pedido (``order``) e, se permitida, troca ``order.state`` por um estado NOVO."""

    name = "?"

    def pay(self, order: "Order") -> None:
        raise NotImplementedError

    def ship(self, order: "Order") -> None:
        raise NotImplementedError

    def deliver(self, order: "Order") -> None:
        raise NotImplementedError

    def cancel(self, order: "Order") -> None:
        raise NotImplementedError


class New(State):
    """``name = "new"``. ``pay`` -> ``Paid``; ``cancel`` -> ``Cancelled``; o resto é negado."""


class Paid(State):
    """``name = "paid"``. ``ship`` -> ``Shipped``; ``cancel`` -> ``Cancelled`` (e marca ``order.refund = True``); o resto é negado."""


class Shipped(State):
    """``name = "shipped"``. ``deliver`` -> ``Delivered``; o resto é negado (um pedido enviado não se cancela)."""


class Delivered(State):
    """``name = "delivered"``. Terminal: tudo é negado."""


class Cancelled(State):
    """``name = "cancelled"``. Terminal: tudo é negado."""


class Order:
    """O CONTEXTO. ``Order()`` começa em ``New``, com ``refund = False``. ``pay()``, ``ship()``, ``deliver()`` e ``cancel()`` DELEGAM ao estado atual (passando ``self``);
    ``state_name`` devolve o ``name`` do estado atual; ``history`` é a lista (cópia) dos nomes dos estados por onde passou, começando por ``"new"``; uma transição negada
    NÃO altera nada (nem a história); ``is_final`` é verdadeiro em ``delivered`` e ``cancelled``."""

    def __init__(self):
        raise NotImplementedError

    def pay(self) -> None:
        raise NotImplementedError

    def ship(self) -> None:
        raise NotImplementedError

    def deliver(self) -> None:
        raise NotImplementedError

    def cancel(self) -> None:
        raise NotImplementedError

    @property
    def state_name(self) -> str:
        raise NotImplementedError

    @property
    def history(self) -> list[str]:
        raise NotImplementedError

    @property
    def is_final(self) -> bool:
        raise NotImplementedError
