import weakref

import pytest


def test_temperature_properties(load_exercise):
    Temperature = load_exercise("ex01_temperature").Temperature
    t = Temperature(100)
    assert t.celsius == 100 and t.fahrenheit == 212 and round(t.kelvin, 2) == 373.15
    t.fahrenheit = 32
    assert round(t.celsius, 6) == 0
    t.celsius = 21.5
    assert repr(t) == "Temperature(celsius=21.5)"
    assert Temperature.celsius.__doc__ == "Temperatura em Celsius."
    assert isinstance(Temperature.celsius, property)


def test_temperature_validation_and_readonly(load_exercise):
    Temperature = load_exercise("ex01_temperature").Temperature
    with pytest.raises(ValueError):
        Temperature(-300)
    t = Temperature(0)
    with pytest.raises(ValueError):
        t.celsius = -273.16
    with pytest.raises(ValueError):
        t.fahrenheit = -1000
    with pytest.raises(AttributeError):
        t.kelvin = 1
    assert t.celsius == 0                      # nada foi alterado pelos erros


def _product_class(module):
    class Product:
        name = module.NonEmpty()
        price = module.Positive()
        unit = module.OneOf("kg", "un")

        def __init__(self, name, price, unit):
            self.name, self.price, self.unit = name, price, unit

    return Product


def test_validators_accept_and_reject(load_exercise):
    module = load_exercise("ex02_validators")
    Product = _product_class(module)
    apple = Product("maçã", 4.5, "kg")
    assert (apple.name, apple.price, apple.unit) == ("maçã", 4.5, "kg")
    for kwargs in ({"name": "  ", "price": 1, "unit": "kg"},
                   {"name": "x", "price": 0, "unit": "kg"},
                   {"name": "x", "price": True, "unit": "kg"},
                   {"name": "x", "price": 1, "unit": "m"},
                   {"name": 5, "price": 1, "unit": "kg"}):
        with pytest.raises(ValueError):
            Product(**kwargs)
    with pytest.raises(ValueError, match="price"):
        apple.price = -1
    assert apple.price == 4.5


def test_validators_state_is_per_instance(load_exercise):
    module = load_exercise("ex02_validators")
    Product = _product_class(module)
    a, b = Product("a", 1, "kg"), Product("b", 2, "un")
    assert (a.price, b.price) == (1, 2)
    a.price = 10
    assert (a.price, b.price) == (10, 2)
    assert isinstance(Product.price, module.Positive)
    assert Product.price is Product.__dict__["price"]


def test_validators_work_in_other_classes(load_exercise):
    module = load_exercise("ex02_validators")

    class Rect:
        width = module.Positive()
        height = module.Positive()

        def __init__(self, width, height):
            self.width, self.height = width, height

    r = Rect(2, 3)
    with pytest.raises(ValueError, match="height"):
        r.height = 0
    assert (r.width, r.height) == (2, 3)


def test_my_property_as_decorator(load_exercise):
    my_property = load_exercise("ex03_my_property").my_property

    class Circle:
        def __init__(self, radius):
            self._radius = radius

        @my_property
        def radius(self):
            """Raio do círculo."""
            return self._radius

        @radius.setter
        def radius(self, value):
            if value < 0:
                raise ValueError("negativo")
            self._radius = value

        @radius.deleter
        def radius(self):
            del self._radius

        @my_property
        def area(self):
            return 3 * self._radius ** 2

    c = Circle(2)
    assert c.radius == 2 and c.area == 12
    c.radius = 5
    assert c.radius == 5
    with pytest.raises(ValueError):
        c.radius = -1
    with pytest.raises(AttributeError):
        c.area = 1
    with pytest.raises(AttributeError):
        del c.area
    del c.radius
    assert not hasattr(c, "_radius")
    assert Circle.radius.__doc__ == "Raio do círculo."
    assert isinstance(Circle.radius, my_property)
    assert hasattr(my_property, "__set__") and hasattr(my_property, "__get__")


def test_lazy_descriptor(load_exercise):
    lazy = load_exercise("ex04_lazy").lazy

    class Report:
        def __init__(self):
            self.calls = 0

        @lazy
        def total(self):
            """Soma cara."""
            self.calls += 1
            return 42

    r = Report()
    assert "total" not in vars(r)
    assert r.total == 42 and r.total == 42 and r.calls == 1
    assert vars(r)["total"] == 42
    del r.total
    assert r.total == 42 and r.calls == 2
    assert isinstance(Report.total, lazy) and Report.total.__doc__ == "Soma cara."
    assert not hasattr(lazy, "__set__")
    other = Report()
    assert other.total == 42 and other.calls == 1


def test_make_record_slots(load_exercise):
    make_record = load_exercise("ex05_slots_factory").make_record
    Point = make_record("Point", ["x", "y"])
    p = Point(1, y=2)
    assert (p.x, p.y) == (1, 2) and repr(p) == "Point(x=1, y=2)"
    assert p == Point(1, 2) and p != Point(1, 3) and p != (1, 2)
    assert not hasattr(p, "__dict__")
    with pytest.raises(AttributeError):
        p.z = 3
    with pytest.raises(TypeError):
        Point(1)
    with pytest.raises(TypeError):
        Point(1, 2, 3)
    assert Point.__slots__ == ("x", "y") and Point.__name__ == "Point"


def test_make_record_weakref(load_exercise):
    make_record = load_exercise("ex05_slots_factory").make_record
    plain = make_record("A", ["a"])
    weak = make_record("B", ["a"], weakref=True)
    with pytest.raises(TypeError):
        weakref.ref(plain(1))
    obj = weak(1)
    assert weakref.ref(obj)() is obj
