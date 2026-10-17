from customers import Customer


class Order:
    def __init__(self, customer: Customer) -> None:
        self.customer = customer
