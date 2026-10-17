import time

import pytest


class FakeClock:
    def __init__(self, steps):
        self.steps = list(steps)
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.steps.pop(0)


def test_timer_with_fake_clock(load_exercise):
    Timer = load_exercise("ex01_timer").Timer
    clock = FakeClock([1_000, 3_500_000_000])
    with Timer(clock) as t:
        pass
    assert t.elapsed_ns == 3_499_999_000 and t.elapsed == pytest.approx(3.499999)


def test_timer_running_and_exception(load_exercise):
    Timer = load_exercise("ex01_timer").Timer
    ticks = iter([0, 500, 2000, 9000])
    t = Timer(lambda: next(ticks))
    with t:
        assert t.elapsed_ns == 500                                           # já mostra o decorrido até aqui
    assert t.elapsed_ns > 0
    ticks2 = iter([10, 40])
    t2 = Timer(lambda: next(ticks2))
    with pytest.raises(RuntimeError):
        with t2:
            raise RuntimeError
    assert t2.elapsed_ns == 30


def test_timer_real_clock(load_exercise):
    Timer = load_exercise("ex01_timer").Timer
    with Timer() as t:
        time.sleep(0.02)
    assert 0.015 <= t.elapsed < 0.5 and isinstance(t.elapsed_ns, int)


def test_benchmark_statistics(load_exercise):
    benchmark = load_exercise("ex01_timer").benchmark
    # 3 rodadas de 4 chamadas; relógio falso: início/fim de cada rodada
    clock = FakeClock([0, 8_000_000_000, 8_000_000_000, 12_000_000_000, 12_000_000_000, 24_000_000_000])
    calls = []
    result = benchmark(lambda x, y=0: calls.append((x, y)), 1, y=2, repeat=3, number=4, clock_ns=clock)
    assert len(calls) == 12 and calls[0] == (1, 2)
    assert result["runs"] == [2.0, 1.0, 3.0] and result["min"] == 1.0 and result["median"] == 2.0
    assert result["mean"] == 2.0 and result["stdev"] == pytest.approx(1.0)


def test_benchmark_edge_cases(load_exercise):
    benchmark = load_exercise("ex01_timer").benchmark
    assert benchmark(lambda: None, repeat=1, number=1)["stdev"] == 0.0
    for kwargs in ({"repeat": 0}, {"number": 0}):
        with pytest.raises(ValueError):
            benchmark(lambda: None, **kwargs)


def test_estimate_exponent(load_exercise):
    m = load_exercise("ex02_scaling")
    sizes = [100, 200, 400, 800]
    assert m.estimate_exponent(sizes, [n * 0.001 for n in sizes]) == pytest.approx(1.0, abs=1e-9)
    assert m.estimate_exponent(sizes, [n**2 * 1e-6 for n in sizes]) == pytest.approx(2.0, abs=1e-9)
    assert m.estimate_exponent(sizes, [5.0] * 4) == pytest.approx(0.0, abs=1e-9)
    for bad in (([1], [1]), ([1, 2], [1]), ([1, 0], [1, 1]), ([1, 2], [1, -1])):
        with pytest.raises(ValueError):
            m.estimate_exponent(*bad)


def test_classify(load_exercise):
    classify = load_exercise("ex02_scaling").classify
    assert [classify(k) for k in (0.0, 0.29, 0.3, 1.0, 1.39, 1.4, 2.0, 2.39, 2.4, 3.0)] == [
        "constante", "constante", "linear", "linear", "linear", "quadrática", "quadrática", "quadrática",
        "cúbica ou pior", "cúbica ou pior"]


def test_measure_scaling_with_synthetic_clock(load_exercise):
    m = load_exercise("ex02_scaling")
    state = {"now": 0.0, "cost": 0.0}

    def clock():
        return state["now"]

    def func(n):
        state["now"] += n * n * 1e-6                           # custo quadrático simulado

    exponent, times = m.measure_scaling(func, lambda n: n, [10, 20, 40, 80], repeat=2, clock=clock)
    assert exponent == pytest.approx(2.0, abs=1e-6) and times[0] == pytest.approx(1e-4)
    seen = []
    ticks = iter(range(1, 1000))
    m.measure_scaling(lambda x: None, lambda n: seen.append(n) or n, [5, 7], repeat=3, clock=lambda: next(ticks))
    assert seen == [5, 7]                                      # a entrada é gerada UMA vez por tamanho


def test_profile_function(load_exercise):
    m = load_exercise("ex03_profile")

    def helper():
        return sum(i * i for i in range(20_000))

    def work():
        total = 0
        for _ in range(5):
            total += helper()
        return total

    result, rows = m.profile_function(work, top=3)
    assert result == 5 * helper() and len(rows) <= 3
    assert rows == sorted(rows, key=lambda r: r[2], reverse=True)
    names = [r[0] for r in rows]
    assert "<genexpr>" in names and next(r for r in rows if r[0] == "<genexpr>")[1] >= 5


def test_call_counts(load_exercise):
    m = load_exercise("ex03_profile")

    def leaf(x):
        return x + 1

    def middle(x):
        return leaf(x) + leaf(x * 2)

    def root():
        return [middle(i) for i in range(4)]

    counts = m.call_counts(root)
    assert counts["leaf"] == 8 and counts["middle"] == 4 and counts["root"] == 1
    assert all(not name.startswith("{") for name in counts)
    assert m.call_counts(lambda: None) == {"<lambda>": 1}


def test_measure_peak(load_exercise):
    import tracemalloc
    m = load_exercise("ex04_memory")
    result, peak = m.measure_peak(lambda n: [0] * n, 1_000_000)
    assert len(result) == 1_000_000 and 7_000_000 < peak < 12_000_000 and not tracemalloc.is_tracing()
    _, small = m.measure_peak(lambda: 1 + 1)
    assert small < 10_000
    tracemalloc.start()
    try:
        m.measure_peak(lambda: bytearray(200_000))
        assert tracemalloc.is_tracing()                       # respeitou o estado anterior
    finally:
        tracemalloc.stop()


def test_top_allocations(load_exercise):
    m = load_exercise("ex04_memory")

    def allocate():
        big = bytearray(3_000_000)
        small = [object() for _ in range(10)]
        return big, small

    rows = m.top_allocations(allocate, limit=2)
    assert 1 <= len(rows) <= 2 and rows[0][1] >= 3_000_000
    assert rows[0][0].startswith("test_cap09.py:") or ":" in rows[0][0]
    assert rows == sorted(rows, key=lambda r: r[1], reverse=True)


def test_retains_memory(load_exercise):
    m = load_exercise("ex04_memory")
    store = []
    assert m.retains_memory(lambda: store.append("x" * 10_000)) is True
    assert m.retains_memory(lambda: "x" * 10_000) is False
    assert m.retains_memory(lambda: [i for i in range(5_000)]) is False


def timeit_once(func, *args, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        best = min(best, time.perf_counter() - start)
    return best


def test_optimized_results_match(load_exercise):
    m = load_exercise("ex05_optimize")
    items = [3, 1, 3, 2, 1, "a", "a", (1, 2), (1, 2)]
    assert m.unique_fast(items) == m.unique_naive(items) and m.unique_fast([]) == []
    a, b = [5, 1, 5, 2, 9, 1], [1, 5, 7]
    assert m.common_fast(a, b) == m.common_naive(a, b) == [5, 1, 5, 1]
    nums = [1, 2, 3, 4, 3, 2, 1, 5, 5]
    for target in (4, 5, 6, 10, 99):
        assert m.pair_count_fast(nums, target) == m.pair_count_naive(nums, target)
    words = "a b a c b a d".split()
    assert m.frequencies_fast(words) == m.frequencies_naive(words) and list(m.frequencies_fast(words)) == ["a", "b", "c", "d"]
    assert [m.fib_fast(n) for n in range(15)] == [m.fib_naive(n) for n in range(15)]
    assert m.fib_fast(5000) % 1_000_007 == m.fib_fast(5000) % 1_000_007 and m.fib_fast(90) == 2880067194370816120


@pytest.mark.parametrize("name, make_args, naive_n", [
    ("unique", lambda n: ([i % (n // 3) for i in range(n)],), 6_000),
    ("common", lambda n: (list(range(n)), list(range(0, n * 2, 2))), 6_000),
    ("pair_count", lambda n: (list(range(n)), n), 1_500),
    ("frequencies", lambda n: (["w%d" % (i % (n // 2)) for i in range(n)],), 4_000),
])
def test_optimized_is_much_faster(load_exercise, name, make_args, naive_n):
    m = load_exercise("ex05_optimize")
    naive, fast = getattr(m, f"{name}_naive"), getattr(m, f"{name}_fast")
    args = make_args(naive_n)
    assert fast(*args) == naive(*args)
    assert timeit_once(naive, *args) / timeit_once(fast, *args) > 8


def test_fib_fast_is_instant(load_exercise):
    fib_fast = load_exercise("ex05_optimize").fib_fast
    assert timeit_once(fib_fast, 4000) < 0.05


def test_sampler_finds_hot_function(load_exercise):
    m = load_exercise("ex06_sampler")

    def slow_part():
        end = time.perf_counter() + 0.5
        while time.perf_counter() < end:
            pass

    def fast_part():
        time.sleep(0)

    def program():
        slow_part()
        for _ in range(100):
            fast_part()
        return "done"

    result, counter = m.sample_profile(program, interval=0.001)
    assert result == "done" and sum(counter.values()) >= 5
    name, fraction = m.hottest(counter)[0]
    assert name == "slow_part" and fraction > 0.7


def test_sampler_stops_thread_and_propagates(load_exercise):
    import threading
    m = load_exercise("ex06_sampler")
    before = threading.active_count()

    def boom():
        time.sleep(0.01)
        raise ValueError("falhou")

    with pytest.raises(ValueError):
        m.sample_profile(boom)
    assert threading.active_count() == before
    from collections import Counter
    assert m.hottest(Counter({"a": 3, "b": 1}), n=2) == [("a", 0.75), ("b", 0.25)] and m.hottest(Counter()) == []
