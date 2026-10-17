from orders import Order   # <- precisa de orders inteiro


class Customer:
    def __init__(self, name: str) -> None:
        self.name = name
        self.orders: list[Order] = []
