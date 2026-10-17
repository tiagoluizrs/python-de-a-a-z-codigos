import math
import time

import pytest
import tasks


def test_amdahl(load_exercise):
    m = load_exercise("ex01_amdahl")
    assert m.amdahl_speedup(0.5, 2) == pytest.approx(4 / 3) and m.amdahl_speedup(1.0, 8) == pytest.approx(8) and m.amdahl_speedup(0, 8) == 1
    assert m.amdahl_speedup(0.9, 1) == pytest.approx(1) and m.amdahl_speedup(0.95, 20) == pytest.approx(1 / (0.05 + 0.95 / 20))
    assert m.efficiency(0.5, 2) == pytest.approx(2 / 3) and m.efficiency(1.0, 4) == pytest.approx(1)
    for args in ((1.1, 2), (-0.1, 2), (0.5, 0)):
        with pytest.raises(ValueError):
            m.amdahl_speedup(*args)


def test_limits_and_gustafson(load_exercise):
    m = load_exercise("ex01_amdahl")
    assert m.max_speedup(0.5) == pytest.approx(2) and m.max_speedup(0.9) == pytest.approx(10) and m.max_speedup(1.0) == math.inf and m.max_speedup(0) == 1
    assert m.gustafson_speedup(0.9, 10) == pytest.approx(9.1) and m.gustafson_speedup(0, 10) == 1 and m.gustafson_speedup(1, 10) == 10


def test_best_worker_count(load_exercise):
    m = load_exercise("ex01_amdahl")
    assert m.best_worker_count(0) == 1 and m.best_worker_count(1.0, limit=16) == 16
    n = m.best_worker_count(0.9, minimum_efficiency=0.5)
    assert m.efficiency(0.9, n) >= 0.5 > m.efficiency(0.9, n + 1) and n == 11
    assert m.best_worker_count(0.95, minimum_efficiency=0.8) < m.best_worker_count(0.95, minimum_efficiency=0.5)


def test_cpu_ratio_with_fake_clocks(load_exercise):
    m = load_exercise("ex02_classify")
    wall = iter([0.0, 10.0])
    cpu = iter([0.0, 2.5])
    ratio, result = m.cpu_ratio(lambda x: x * 2, 21, clock=lambda: next(wall), cpu_clock=lambda: next(cpu))
    assert ratio == pytest.approx(0.25) and result == 42
    zero = iter([1.0, 1.0])
    assert m.cpu_ratio(lambda: None, clock=lambda: next(zero), cpu_clock=lambda: 0.0)[0] == 0.0


def test_classify_thresholds(load_exercise):
    classify = load_exercise("ex02_classify").classify
    assert [classify(r) for r in (0.0, 0.3, 0.31, 0.79, 0.8, 1.0)] == ["io", "io", "mixed", "mixed", "cpu", "cpu"]
    assert classify(0.5, cpu_threshold=0.5) == "cpu" and classify(0.5, io_threshold=0.6) == "io"


def test_classify_real_functions(load_exercise):
    m = load_exercise("ex02_classify")
    assert m.classify_function(time.sleep, 0.15)[0] == "io"
    kind, ratio = m.classify_function(tasks.cpu_task, 2_500_000)
    assert kind == "cpu" and ratio > 0.8


def test_compare_models(load_exercise):
    m = load_exercise("ex03_compare_models")
    report = m.compare_models(tasks.io_task, [0.05] * 8, workers=8, models=("sequential", "threads"))
    assert set(report) == {"sequential", "threads"} and report["sequential"]["results"] == [0.05] * 8
    gains = m.speedups(report)
    assert set(gains) == {"threads"} and gains["threads"] > 2.5 and m.results_agree(report)


def test_compare_models_processes_and_order(load_exercise):
    m = load_exercise("ex03_compare_models")
    items = list(range(12))
    report = m.compare_models(tasks.square, items, workers=3)
    assert set(report) == {"sequential", "threads", "processes"}
    assert all(data["results"] == [i * i for i in items] for data in report.values()) and m.results_agree(report)
    report["threads"]["results"] = [0]
    assert m.results_agree(report) is False


def test_compare_models_unknown(load_exercise):
    m = load_exercise("ex03_compare_models")
    start = time.perf_counter()
    with pytest.raises(ValueError):
        m.compare_models(tasks.io_task, [0.2, 0.2], models=("sequential", "gpu"))
    assert time.perf_counter() - start < 0.1


@pytest.mark.parametrize("args, expected", [
    (dict(cpu_bound=False, items=1), "none"), (dict(cpu_bound=True, items=0), "none"), (dict(cpu_bound=True, items=100), "processes"),
    (dict(cpu_bound=True, items=100, shared_state=True), "free-threading"), (dict(cpu_bound=False, items=20), "threads"),
    (dict(cpu_bound=False, items=501, async_library=True), "asyncio"), (dict(cpu_bound=False, items=500, async_library=True), "threads"),
    (dict(cpu_bound=False, items=9000), "threads")])
def test_recommend(load_exercise, args, expected):
    assert load_exercise("ex04_recommend").recommend(**args) == expected


def test_explain_and_errors(load_exercise):
    m = load_exercise("ex04_recommend")
    assert m.explain(True, 100) == "processes: carga de CPU com 100 itens"
    assert m.explain(False, 1000, async_library=True) == "asyncio: carga de E/S com 1000 itens" and m.explain(False, 1) == "none: nada a paralelizar"
    with pytest.raises(ValueError):
        m.recommend(True, -1)


def test_scheduler_math(load_exercise):
    m = load_exercise("ex05_scheduler_math")
    assert m.pool_size(100, 0.2) == 20 and m.pool_size(100, 0.2, utilization=0.5) == 40 and m.pool_size(3, 0.1) == 1 and m.pool_size(0, 0.1) == 1
    assert m.pool_size(10, 0.25) == 3                                        # 2.5 arredonda para cima
    for u in (0, 1.5, -1):
        with pytest.raises(ValueError):
            m.pool_size(1, 1, utilization=u)
    assert m.throughput(8, 0.1) == pytest.approx(80) and m.total_time(50, 8, 0.1) == pytest.approx(0.7) and m.total_time(16, 8, 1) == 2 and m.total_time(0, 4, 1) == 0
