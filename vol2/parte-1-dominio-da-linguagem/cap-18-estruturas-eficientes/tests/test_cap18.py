import random

import pytest


def test_lru_cache(load_exercise):
    LRUCache = load_exercise("ex01_lru_cache").LRUCache
    with pytest.raises(ValueError):
        LRUCache(0)
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1 and cache.keys() == ["b", "a"]
    cache.put("c", 3)                                    # despeja b
    assert "b" not in cache and cache.get("b", "x") == "x" and len(cache) == 2
    assert "a" in cache and cache.keys() == ["a", "c"]   # in não altera a ordem
    cache.put("a", 10)                                   # atualizar torna recente
    assert cache.keys() == ["c", "a"] and cache.get("a") == 10


def test_top_k_stream(load_exercise):
    TopK = load_exercise("ex02_top_k").TopK
    top = TopK(3)
    for value in [5, 1, 9, 3, 7, 7, 2]:
        top.add(value)
    assert top.result() == [9, 7, 7] and len(top) == 3
    assert top.result() is not top.result()
    small = TopK(5)
    small.add(1)
    assert small.result() == [1]
    with pytest.raises(ValueError):
        TopK(0)
    data = random.sample(range(10_000), 2_000)
    big = TopK(10)
    for value in data:
        big.add(value)
    assert big.result() == sorted(data, reverse=True)[:10] and len(big._heap) == 10


def test_merge_streams(load_exercise):
    merge = load_exercise("ex02_top_k").merge_sorted_streams
    assert merge([1, 4], [2, 3], iter([0, 9])) == [0, 1, 2, 3, 4, 9] and merge() == []


def test_running_median(load_exercise):
    RunningMedian = load_exercise("ex03_running_median").RunningMedian
    rm = RunningMedian()
    with pytest.raises(ValueError):
        rm.median()
    seen = []
    for value in [5, 15, 1, 3, 8, 7, 9, 10, 20, 2]:
        rm.add(value)
        seen.append(value)
        ordered = sorted(seen)
        n = len(ordered)
        expected = ordered[n // 2] if n % 2 else (ordered[n // 2 - 1] + ordered[n // 2]) / 2
        assert rm.median() == expected
    assert isinstance(rm.median(), float)


def test_bisect_grade_and_insert(load_exercise):
    module = load_exercise("ex04_bisect_tools")
    marks = [60, 70, 80, 90]
    assert [module.grade(s, marks, "FDCBA") for s in (0, 59, 60, 75, 89, 90, 100)] == list("FFDCBAA")
    items = [1, 3, 5]
    assert module.insert_unique(items, 4) is True and module.insert_unique(items, 3) is False
    assert module.insert_unique(items, 0) and module.insert_unique(items, 9) and items == [0, 1, 3, 4, 5, 9]


def test_bisect_range_and_closest(load_exercise):
    module = load_exercise("ex04_bisect_tools")
    data = [1, 3, 3, 5, 8, 13, 21]
    assert module.count_in_range(data, 3, 13) == 5 and module.count_in_range(data, 4, 4) == 0
    assert module.count_in_range(data, 14, 20) == 0 and module.count_in_range(data, 5, 3) == 0
    assert module.closest(data, 6) == 5 and module.closest(data, 7) == 8 and module.closest(data, 100) == 21
    assert module.closest(data, -5) == 1 and module.closest([2, 4], 3) == 2
    with pytest.raises(ValueError):
        module.closest([], 1)


def test_build_layers(load_exercise):
    module = load_exercise("ex05_build_order")
    deps = {"app": {"lib", "log"}, "lib": {"core"}, "log": {"core"}}
    assert module.build_layers(deps) == [["core"], ["lib", "log"], ["app"]]
    assert module.critical_path_length(deps) == 3 and module.critical_path_length({}) == 0
    assert module.build_layers({"a": set(), "b": set()}) == [["a", "b"]]
    with pytest.raises(ValueError, match="ciclo"):
        module.build_layers({"a": {"b"}, "b": {"a"}})


def test_moving_average(load_exercise):
    moving_average = load_exercise("ex06_sliding").moving_average
    assert list(moving_average([1, 2, 3, 4, 5], 3)) == [2.0, 3.0, 4.0]
    assert list(moving_average(iter([10, 20]), 1)) == [10.0, 20.0] and list(moving_average([1], 2)) == []
    with pytest.raises(ValueError):
        list(moving_average([1], 0))


def test_max_sliding_window(load_exercise):
    window = load_exercise("ex06_sliding").max_sliding_window
    assert window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
    assert window([4], 1) == [4] and window([1, 2], 5) == []
    data = [random.randint(0, 100) for _ in range(300)]
    assert window(data, 7) == [max(data[i:i + 7]) for i in range(len(data) - 6)]
