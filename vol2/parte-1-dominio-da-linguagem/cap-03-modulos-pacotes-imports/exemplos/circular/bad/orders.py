from customers import Customer   # <- precisa de customers inteiro


class Order:
    def __init__(self, customer: Customer) -> None:
        self.customer = customer


def make_order(name: str) -> Order:
    return Order(Customer(name))
