"""Quebra o ciclo com import tardio, dentro da funcao."""


class Customer:
    def __init__(self, name: str) -> None:
        self.name = name

    def new_order(self):
        from orders import Order   # so executa quando chamado
        return Order(self)
