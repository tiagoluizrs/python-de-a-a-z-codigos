import random

import pytest


def test_linear_probing_matches_dict(load_exercise):
    Table = load_exercise("ex01_open_addressing").LinearProbingTable
    table, reference = Table(), {}
    rng = random.Random(7)
    for _ in range(3000):
        key = rng.randrange(400)
        action = rng.random()
        if action < 0.6:
            table[key] = key * 2
            reference[key] = key * 2
        elif key in reference:
            del table[key]
            del reference[key]
        else:
            with pytest.raises(KeyError):
                del table[key]
        assert len(table) == len(reference)
    assert set(table) == set(reference)
    assert all(table[k] == v for k, v in reference.items())
    assert all((k in table) for k in reference)
    assert 10**6 not in table


def test_linear_probing_grows_and_survives_tombstones(load_exercise):
    Table = load_exercise("ex01_open_addressing").LinearProbingTable
    table = Table()
    assert table.slots == 8
    for i in range(100):
        table[i] = i
    assert table.slots >= 150 and table.slots & (table.slots - 1) == 0
    for i in range(0, 100, 2):
        del table[i]
    assert sorted(table) == list(range(1, 100, 2))
    for i in range(0, 100, 2):
        table[i] = -i
    assert len(table) == 100 and table[4] == -4
    with pytest.raises(KeyError):
        table["missing"]


def test_point_is_a_good_key(load_exercise):
    Point = load_exercise("ex02_hashable_point").Point
    assert Point(1, 2) == Point(1.0, 2.0)
    assert hash(Point(1, 2)) == hash(Point(1.0, 2.0))
    assert Point(1, 2) != (1, 2)
    assert {Point(1, 2): "a"}[Point(1.0, 2.0)] == "a"
    assert repr(Point(1, 2)) == "Point(1, 2)"
    point = Point(3, 4)
    with pytest.raises(AttributeError):
        point.x = 9
    with pytest.raises(AttributeError):
        point.z = 1
    assert not hasattr(point, "__dict__")


def test_count_eq_calls(load_exercise):
    count = load_exercise("ex03_count_eq_calls").count_eq_calls
    assert count(100, lambda i: i) == 0
    assert count(100, lambda i: 1) == 4950
    assert count(100, lambda i: i % 10) == 450
    assert count(1000, lambda i: 1) == 499_500


def test_lru_cache(load_exercise):
    LRUCache = load_exercise("ex04_lru_cache").LRUCache
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1           # "a" fica mais recente
    cache.put("c", 3)                    # remove "b"
    assert cache.get("b") is None and cache.get("b", 0) == 0
    assert cache.keys() == ["a", "c"]
    cache.put("a", 10)                   # atualiza e renova
    cache.put("d", 4)                    # remove "c"
    assert cache.keys() == ["a", "d"] and len(cache) == 2
    assert cache.get("a") == 10


def test_frozen_map(load_exercise):
    FrozenMap = load_exercise("ex05_frozen_map").FrozenMap
    source = {"a": 1, "b": 2}
    fm = FrozenMap(source)
    source["c"] = 3
    assert len(fm) == 2 and list(fm) == ["a", "b"]
    assert fm["a"] == 1 and fm.get("z", 0) == 0 and "b" in fm
    assert fm == {"a": 1, "b": 2}
    assert dict(fm.items()) == {"a": 1, "b": 2}
    assert hash(fm) == hash(FrozenMap({"b": 2, "a": 1}))
    assert {fm: "ok"}[FrozenMap([("a", 1), ("b", 2)])] == "ok"
    with pytest.raises(TypeError):
        fm["x"] = 1
    with pytest.raises(KeyError):
        fm["x"]
