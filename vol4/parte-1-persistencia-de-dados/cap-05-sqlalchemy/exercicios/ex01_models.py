"""Exercício 1: modelos ORM 2.0 com relacionamentos."""


def build_models():
    """Cria e devolve ``(Base, Customer, Order, OrderLine)``: classes novas a CADA chamada
    (um ``DeclarativeBase`` novo), todas com ``Mapped``/``mapped_column``.

    * ``Customer``: ``id`` PK, ``name`` ``String(60)`` não nulo, ``email`` ``String(120)``
      ÚNICO e não nulo; ``orders`` (lista) com ``cascade="all, delete-orphan"``, ordenada por ``Order.id``;
    * ``Order``: ``id`` PK, ``customer_id`` FK para ``customer.id`` não nulo, ``created_at``
      ``DateTime`` com padrão ``datetime.now(UTC)`` (callable, sem fuso no banco),
      ``customer`` e ``lines`` (``cascade="all, delete-orphan"``, ordenadas por ``OrderLine.id``);
      propriedade ``total`` = soma dos ``subtotal`` das linhas (``Decimal``; ``Decimal("0.00")`` sem linhas);
    * ``OrderLine``: ``id`` PK, ``order_id`` FK não nulo, ``product`` ``String(60)`` não nulo,
      ``quantity`` ``Integer`` com ``CheckConstraint("quantity > 0")``, ``unit_price``
      ``Numeric(10, 2)`` não nulo; propriedade ``subtotal`` = ``quantity * unit_price``;
    * nomes de tabela: ``customer``, ``customer_order`` (``order`` é palavra reservada) e ``order_line``;
    * relacionamentos com ``back_populates`` nas duas pontas."""
    raise NotImplementedError
