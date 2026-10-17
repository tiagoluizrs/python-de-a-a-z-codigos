import dataclasses
import datetime as dt
from decimal import Decimal
from enum import Enum

import pytest


def test_product_is_a_dataclass(load_exercise):
    Product = load_exercise("ex01_product").Product
    assert dataclasses.is_dataclass(Product)
    p = Product("  ab-1 ", "Café Torrado", Decimal("12.50"))
    assert p.sku == "AB-1" and p.slug == "café-torrado" and p.tags == []
    assert "slug" not in repr(p) and "Product(sku='AB-1'" in repr(p)
    names = [f.name for f in dataclasses.fields(Product)]
    assert names == ["sku", "name", "price", "tags", "slug"]
    assert next(f for f in dataclasses.fields(Product) if f.name == "slug").init is False


def test_product_validation_and_independent_tags(load_exercise):
    Product = load_exercise("ex01_product").Product
    with pytest.raises(ValueError):
        Product("x", "  ", Decimal("1"))
    with pytest.raises(ValueError):
        Product("x", "ok", Decimal("-1"))
    a, b = Product("a", "A", Decimal("1")), Product("b", "B", Decimal("1"))
    a.tags.append("novo")
    assert b.tags == [] and a == Product("a", "A", Decimal("1"), ["novo"])


def test_order_is_immutable_aggregate(load_exercise):
    module = load_exercise("ex02_order")
    LineItem, Order = module.LineItem, module.Order
    item = LineItem("a", 2, Decimal("10.50"))
    assert item.total == Decimal("21.00")
    with pytest.raises(dataclasses.FrozenInstanceError):
        item.quantity = 3
    with pytest.raises(ValueError):
        LineItem("a", 0, Decimal("1"))
    empty = Order("ana")
    assert empty.total == Decimal("0") and empty.items == ()
    bigger = empty.add(item).add(LineItem("b", 1, Decimal("4")))
    assert empty.items == () and len(bigger.items) == 2
    assert bigger.total == Decimal("25.00")
    assert hash(bigger) == hash(Order("ana", bigger.items))
    with pytest.raises(dataclasses.FrozenInstanceError):
        bigger.customer = "outro"


def test_tasks_sorting(load_exercise):
    Task = load_exercise("ex03_sorted_tasks").Task
    tasks = [Task(1, "limpar"), Task(5, "deploy"), Task(3, "revisar"), Task(5, "backup")]
    assert [t.name for t in sorted(tasks)] == ["backup", "deploy", "revisar", "limpar"]
    assert "sort_index" not in repr(tasks[0]) and "done" not in repr(tasks[0])
    assert Task(2, "x", done=True) == Task(2, "x", done=False)
    assert max(tasks, key=lambda t: t.priority).priority == 5
    assert Task(5, "a") < Task(1, "a")


def test_customer_kw_only(load_exercise):
    module = load_exercise("ex04_inheritance")
    Entity, Customer = module.Entity, module.Customer
    assert issubclass(Customer, Entity) and dataclasses.is_dataclass(Customer)
    c = Customer(1, name="Ana")
    assert (c.id, c.created, c.name, c.vip) == (1, "hoje", "Ana", False)
    assert Customer(id=2, name="Bia", vip=True, created="ontem").vip is True
    with pytest.raises(TypeError):
        Customer(1, "Ana")
    with pytest.raises(TypeError):
        Customer(1)
    assert Entity(3) == Entity(3, "hoje")


class Color(Enum):
    RED = "r"


def test_to_primitive_basics(load_exercise):
    to_primitive = load_exercise("ex05_serializer").to_primitive

    @dataclasses.dataclass
    class Item:
        name: str
        price: Decimal
        when: dt.date
        secret: str = dataclasses.field(default="x", metadata={"skip": True})
        qty: int = dataclasses.field(default=1, metadata={"name": "quantity"})

    @dataclasses.dataclass
    class Cart:
        items: list
        tags: set
        color: Color
        meta: dict

    cart = Cart([Item("a", Decimal("1.50"), dt.date(2026, 10, 12))],
                {"b", "a"}, Color.RED, {1: (1, 2)})
    assert to_primitive(cart) == {
        "items": [{"name": "a", "price": "1.50", "when": "2026-10-12", "quantity": 1}],
        "tags": ["a", "b"], "color": "r", "meta": {"1": [1, 2]}}


def test_to_primitive_scalars_and_errors(load_exercise):
    to_primitive = load_exercise("ex05_serializer").to_primitive
    assert to_primitive(None) is None and to_primitive(3) == 3 and to_primitive("x") == "x"
    assert to_primitive(dt.datetime(2026, 1, 2, 3, 4)) == "2026-01-02T03:04:00"
    with pytest.raises(TypeError):
        to_primitive(object())
