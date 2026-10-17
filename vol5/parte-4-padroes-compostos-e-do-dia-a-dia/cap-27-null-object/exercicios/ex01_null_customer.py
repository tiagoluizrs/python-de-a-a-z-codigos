"""Exercício 1: o Null Object clássico: a ausência de cliente também é um ``Customer``, e o código que usa o cliente nunca pergunta."""
from abc import ABC, abstractmethod


def money(cents: int) -> str:
    """(Pronto, NÃO edite.) ``1234`` -> ``"R$ 12,34"``."""
    return f"R$ {cents // 100},{cents % 100:02d}"


class Customer(ABC):
    """(Pronto, NÃO edite.) A interface comum."""

    is_null = False

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def discount_pct(self) -> int: ...

    @property
    @abstractmethod
    def points(self) -> int: ...

    @abstractmethod
    def greeting(self) -> str: ...

    @abstractmethod
    def price(self, cents: int) -> int: ...

    @abstractmethod
    def add_points(self, points: int) -> None: ...


class RealCustomer(Customer):
    """``RealCustomer(name, discount_pct=0)``.

    * ``name`` sem espaços nas pontas; vazio: ``ValueError("nome vazio")``; ``discount_pct`` precisa ser um ``int`` de 0 a 100 (``bool`` NÃO vale): ``ValueError("desconto inválido")``;
    * ``points`` começa em ``0``; ``add_points(n)``: ``n`` precisa ser um ``int`` ``> 0`` (``ValueError("pontos inválidos")``) e soma;
    * ``price(cents)``: ``cents`` precisa ser um ``int`` ``>= 0`` (``ValueError("valor inválido")``); devolve ``cents * (100 - desconto) // 100``;
    * ``greeting()``: ``f"Olá, {name}!"``; ``is_null`` é ``False``."""

    def __init__(self, name: str, discount_pct: int = 0):
        raise NotImplementedError


class NullCustomer(Customer):
    """A ausência. Um SINGLETON (``NullCustomer() is NullCustomer()``), sem estado e IMUTÁVEL (qualquer atribuição de atributo levanta ``AttributeError``).

    * ``is_null`` é ``True``; ``name`` é ``"visitante"``; ``discount_pct`` e ``points`` são ``0``; ``bool(NullCustomer())`` é ``False``; ``repr`` é ``"NullCustomer()"``;
    * ``greeting()``: ``"Olá, visitante! Cadastre-se para ganhar descontos."``;
    * ``price(cents)``: valida ``cents`` como o ``RealCustomer`` (``ValueError("valor inválido")``) e devolve ``cents`` (sem desconto);
    * ``add_points(n)``: não faz nada (nem erro) e ``points`` continua ``0``."""


class CustomerRepository:
    """Guarda clientes por id.

    * ``add(customer_id, customer)``: ``customer`` que não é um ``Customer``: ``TypeError``; um ``NullCustomer``: ``ValueError("cliente nulo não pode ser cadastrado")``; id repetido:
      ``ValueError(f"id repetido: {customer_id}")``;
    * ``find(customer_id)``: o cliente, ou o ``NullCustomer`` se o id não existe (NUNCA ``None``);
    * ``find_strict(customer_id)``: o cliente, ou ``KeyError(f"cliente inexistente: {customer_id}")`` (para quando a ausência É um erro);
    * ``names()``: os nomes dos clientes cadastrados em ordem alfabética; ``len(repo)``: quantos há."""

    def __init__(self):
        raise NotImplementedError

    def add(self, customer_id, customer: Customer) -> None:
        raise NotImplementedError

    def find(self, customer_id) -> Customer:
        raise NotImplementedError

    def find_strict(self, customer_id) -> Customer:
        raise NotImplementedError

    def names(self) -> list[str]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class Order:
    """``Order(customer, lines)``: ``lines`` é uma lista de ``(nome, quantidade, valor_unitario_em_centavos)``; quantidade ``int > 0`` (``ValueError("quantidade inválida")``) e valor ``int >= 0``
    (``ValueError("valor inválido")``).

    O ``Order`` NUNCA pergunta ``is_null`` (nem compara o cliente com ``None``): ele usa ``customer`` direto.

    * ``subtotal()``: soma de ``quantidade * valor``; ``total()``: ``customer.price(subtotal)``;
    * ``earn_points()``: calcula ``p = total // 100``; se ``p > 0`` chama ``customer.add_points(p)``; devolve ``p`` (mesmo para o cliente nulo, que apenas ignora);
    * ``summary()``: ``f"{customer.greeting()} Total: {money(total)}"``."""

    def __init__(self, customer: Customer, lines: list):
        raise NotImplementedError

    def subtotal(self) -> int:
        raise NotImplementedError

    def total(self) -> int:
        raise NotImplementedError

    def earn_points(self) -> int:
        raise NotImplementedError

    def summary(self) -> str:
        raise NotImplementedError
