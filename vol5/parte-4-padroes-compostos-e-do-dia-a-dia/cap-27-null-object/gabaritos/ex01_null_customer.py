"""Gabarito do exercício 1."""
from abc import ABC, abstractmethod


def money(cents):
    return f"R$ {cents // 100},{cents % 100:02d}"


def _check_cents(cents):
    if not isinstance(cents, int) or isinstance(cents, bool) or cents < 0:
        raise ValueError("valor inválido")


class Customer(ABC):
    is_null = False

    @property
    @abstractmethod
    def name(self): ...

    @property
    @abstractmethod
    def discount_pct(self): ...

    @property
    @abstractmethod
    def points(self): ...

    @abstractmethod
    def greeting(self): ...

    @abstractmethod
    def price(self, cents): ...

    @abstractmethod
    def add_points(self, points): ...


class RealCustomer(Customer):
    def __init__(self, name, discount_pct=0):
        if not name.strip():
            raise ValueError("nome vazio")
        if not isinstance(discount_pct, int) or isinstance(discount_pct, bool) or not 0 <= discount_pct <= 100:
            raise ValueError("desconto inválido")
        self._name, self._discount_pct, self._points = name.strip(), discount_pct, 0

    @property
    def name(self):
        return self._name

    @property
    def discount_pct(self):
        return self._discount_pct

    @property
    def points(self):
        return self._points

    def greeting(self):
        return f"Olá, {self._name}!"

    def price(self, cents):
        _check_cents(cents)
        return cents * (100 - self._discount_pct) // 100

    def add_points(self, points):
        if not isinstance(points, int) or isinstance(points, bool) or points <= 0:
            raise ValueError("pontos inválidos")
        self._points += points


class NullCustomer(Customer):
    _instance = None
    is_null = True
    name = "visitante"
    discount_pct = 0
    points = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __setattr__(self, name, value):
        raise AttributeError("NullCustomer é imutável")

    def __bool__(self):
        return False

    def __repr__(self):
        return "NullCustomer()"

    def greeting(self):
        return "Olá, visitante! Cadastre-se para ganhar descontos."

    def price(self, cents):
        _check_cents(cents)
        return cents

    def add_points(self, points):
        pass


class CustomerRepository:
    def __init__(self):
        self._customers = {}

    def add(self, customer_id, customer):
        if not isinstance(customer, Customer):
            raise TypeError("precisa ser um Customer")
        if customer.is_null:
            raise ValueError("cliente nulo não pode ser cadastrado")
        if customer_id in self._customers:
            raise ValueError(f"id repetido: {customer_id}")
        self._customers[customer_id] = customer

    def find(self, customer_id):
        return self._customers.get(customer_id, NullCustomer())

    def find_strict(self, customer_id):
        try:
            return self._customers[customer_id]
        except KeyError:
            raise KeyError(f"cliente inexistente: {customer_id}") from None

    def names(self):
        return sorted(c.name for c in self._customers.values())

    def __len__(self):
        return len(self._customers)


class Order:
    def __init__(self, customer, lines):
        for _, qty, unit in lines:
            if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
                raise ValueError("quantidade inválida")
            _check_cents(unit)
        self.customer, self.lines = customer, list(lines)

    def subtotal(self):
        return sum(qty * unit for _, qty, unit in self.lines)

    def total(self):
        return self.customer.price(self.subtotal())

    def earn_points(self):
        points = self.total() // 100
        if points > 0:
            self.customer.add_points(points)
        return points

    def summary(self):
        return f"{self.customer.greeting()} Total: {money(self.total())}"
