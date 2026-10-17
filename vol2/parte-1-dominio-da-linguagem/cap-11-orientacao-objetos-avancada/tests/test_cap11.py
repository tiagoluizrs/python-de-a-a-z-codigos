import pickle

import pytest


def test_tracker_instances_and_counter(load_exercise):
    Tracker = load_exercise("ex01_registry").Tracker
    Tracker.reset_count()
    a, b = Tracker("a"), Tracker("b")
    a.record("x")
    a.record("y")
    b.record("z")
    assert a.events == ["x", "y"] and b.events == ["z"]
    assert a.events is not b.events
    assert Tracker.created_count() == 2
    assert "created" not in vars(a)            # o contador mora na classe
    Tracker.reset_count()
    assert Tracker.created_count() == 0


def test_tracker_static(load_exercise):
    Tracker = load_exercise("ex01_registry").Tracker
    assert Tracker.is_valid_name("ok") and Tracker("x").is_valid_name("ok")
    assert not Tracker.is_valid_name("") and not Tracker.is_valid_name(" a")
    assert not Tracker.is_valid_name("a ")


def test_temperature_constructors(load_exercise):
    Temperature = load_exercise("ex02_temperature").Temperature
    boiling = Temperature.from_celsius(100)
    assert round(boiling.kelvin, 2) == 373.15
    assert round(Temperature.from_fahrenheit(32).celsius(), 6) == 0
    assert round(boiling.fahrenheit(), 6) == 212
    assert repr(Temperature(300.15)) == "Temperature(300.15)"
    with pytest.raises(ValueError):
        Temperature(-1)


def test_temperature_subclass(load_exercise):
    Temperature = load_exercise("ex02_temperature").Temperature

    class Precise(Temperature):
        pass

    result = Precise.from_celsius(0)
    assert type(result) is Precise and repr(result) == "Precise(273.15)"
    assert type(Precise.from_fahrenheit(32)) is Precise


def test_color_flyweight(load_exercise):
    Color = load_exercise("ex03_flyweight").Color
    assert Color("red") is Color("red") is Color("RED")
    assert Color("blue") is not Color("red")
    assert Color.count() >= 2
    before = Color.count()
    Color("green")
    Color("GREEN")
    assert Color.count() == before + 1
    assert repr(Color("red")) == "Color('red')"
    with pytest.raises(ValueError):
        Color("")


def test_point_is_a_tuple(load_exercise):
    Point = load_exercise("ex04_point").Point
    p = Point(1, 2)
    assert p == (1, 2) and p.x == 1 and p.y == 2 and len(p) == 2
    x, y = p
    assert (x, y) == (1, 2) and hash(p) == hash((1, 2))
    assert repr(p) == "Point(x=1, y=2)"
    assert p.moved(2, 3) == Point(3, 5) and isinstance(p.moved(1, 1), Point)
    assert not hasattr(p, "__dict__")
    with pytest.raises(AttributeError):
        p.z = 3
    with pytest.raises(TypeError):
        Point("a", 2)
    with pytest.raises(TypeError):
        Point(True, 2)


def test_bounded_stack(load_exercise):
    BoundedStack = load_exercise("ex05_stack").BoundedStack
    stack = BoundedStack(3)
    assert not stack and len(stack) == 0
    stack.push(1)
    stack.push(2)
    assert stack and len(stack) == 2 and stack.peek() == 2
    assert list(stack) == [2, 1]
    assert repr(stack) == "BoundedStack([1, 2], capacity=3)"
    stack.push(3)
    with pytest.raises(OverflowError):
        stack.push(4)
    assert stack.pop() == 3 and stack.pop() == 2 and stack.pop() == 1
    with pytest.raises(IndexError):
        stack.pop()
    with pytest.raises(IndexError):
        stack.peek()


def test_bounded_stack_is_composition(load_exercise):
    BoundedStack = load_exercise("ex05_stack").BoundedStack
    stack = BoundedStack(2)
    assert not isinstance(stack, list)
    assert not hasattr(stack, "append") and not hasattr(stack, "insert")
    assert any(isinstance(value, list) and name.startswith("_")
               for name, value in vars(stack).items())
