import asyncio
import copy
import io
import logging
import math
import random
import threading
import time

import pytest


# ---------- ex01 ----------
def test_counter(load_exercise):
    m = load_exercise("ex01_metrics")
    c = m.Counter("shop_requests", ("route", "status"))
    c.inc(route="/a", status="200")
    c.inc(2, route="/a", status="200")
    c.inc(route="/a", status="500")
    assert c.value(route="/a", status="200") == 3.0 and c.value(route="/a", status="500") == 1.0 and c.value(route="/b", status="200") == 0.0
    with pytest.raises(ValueError):
        c.inc(-1, route="/a", status="200")
    with pytest.raises(ValueError):
        c.inc(route="/a")
    with pytest.raises(ValueError):
        c.value(route="/a", status="200", extra="x")


def test_counter_is_thread_safe(load_exercise):
    m = load_exercise("ex01_metrics")
    c = m.Counter("n")
    threads = [threading.Thread(target=lambda: [c.inc() for _ in range(5000)]) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert c.value() == 40_000.0


def test_histogram_counts_and_quantile(load_exercise):
    m = load_exercise("ex01_metrics")
    h = m.Histogram("lat", [0.01, 0.05, 0.1, 0.5, 1.0])
    for v in (0.004, 0.012, 0.03, 0.03, 0.2, 0.7):
        h.observe(v)
    assert h.counts() == [1, 4, 4, 5, 6, 6]
    assert h.quantile(0.5) == pytest.approx(0.01 + (0.05 - 0.01) * (3 - 1) / (4 - 1))     # rank 3 cai no bucket (0.01, 0.05]
    assert h.quantile(0.95) == pytest.approx(0.5 + 0.5 * (5.7 - 5) / (6 - 5))              # rank 5,7 cai no bucket (0.5, 1.0]
    assert math.isnan(m.Histogram("x", [1.0]).quantile(0.5))
    big = m.Histogram("big", [1.0, 2.0])
    big.observe(99)
    assert big.quantile(0.9) == 2.0 and big.counts() == [0, 0, 1]


def test_histogram_validation_and_labels(load_exercise):
    m = load_exercise("ex01_metrics")
    for bad in ([], [1, 1], [2, 1]):
        with pytest.raises(ValueError):
            m.Histogram("h", bad)
    h = m.Histogram("h", [1.0, 2.0], ("route",))
    h.observe(1.5, route="/a")
    assert h.counts(route="/a") == [0, 1, 1] and h.counts(route="/b") == [0, 0, 0]
    with pytest.raises(ValueError):
        h.observe(1.0)


def test_render(load_exercise):
    m = load_exercise("ex01_metrics")
    c = m.Counter("shop_requests", ("route", "status"))
    c.inc(2, route="/b", status="200")
    c.inc(route="/a", status="500")
    plain = m.Counter("up")
    plain.inc()
    h = m.Histogram("lat", [0.1, 1.0], ("route",))
    h.observe(0.05, route="/a")
    h.observe(0.5, route="/a")
    text = m.render([c, plain, h])
    assert text.endswith("\n")
    assert text.splitlines() == [
        "# TYPE shop_requests counter",
        'shop_requests_total{route="/a",status="500"} 1.0',
        'shop_requests_total{route="/b",status="200"} 2.0',
        "# TYPE up counter",
        "up_total 1.0",
        "# TYPE lat histogram",
        'lat_bucket{route="/a",le="0.1"} 1',
        'lat_bucket{route="/a",le="1.0"} 2',
        'lat_bucket{route="/a",le="+Inf"} 2',
        'lat_sum{route="/a"} 0.55',
        'lat_count{route="/a"} 2',
    ]


# ---------- ex02 ----------
def test_redact_keys_and_text(load_exercise):
    m = load_exercise("ex02_redact")
    data = {"user": "ana", "Password": "hunter2", "Authorization": "Bearer abc.def-1", "note": "usou Bearer tok_123.x e escreveu para ana@exemplo.com",
            "nested": {"api_key": {"a": 1}, "ok": [1, "bob@site.org", None, True]}, "pair": ("token-x", 3)}
    before = copy.deepcopy(data)
    out = m.redact(data)
    assert data == before                                                  # o original não mudou
    assert out["Password"] == "***" and out["Authorization"] == "***" and out["nested"]["api_key"] == "***"
    assert out["note"] == "usou Bearer *** e escreveu para a***@exemplo.com"
    assert out["nested"]["ok"] == [1, "b***@site.org", None, True] and out["pair"] == ("token-x", 3) and out["user"] == "ana"
    assert isinstance(out["pair"], tuple) and isinstance(out["nested"]["ok"], list)


def test_redact_truncates_after_redacting(load_exercise):
    m = load_exercise("ex02_redact")
    long = "x" * 50
    assert m.redact(long, max_len=20) == "x" * 20 + "…(+30 chars)"
    assert m.redact("Bearer " + "a" * 100 + " fim", max_len=200) == "Bearer *** fim"
    assert m.redact(("a", 1.5, None)) == ("a", 1.5, None) and m.redact(7) == 7


def test_redact_event_processor(load_exercise):
    m = load_exercise("ex02_redact")
    event = {"event": "login", "password": "x", "email": "ana@exemplo.com"}
    out = m.redact_event(None, "info", event)
    assert out == {"event": "login", "password": "***", "email": "a***@exemplo.com"}


# ---------- ex03 ----------
def test_budget_and_burn(load_exercise):
    m = load_exercise("ex03_slo")
    assert m.error_budget(43_200_000, 0.999) == pytest.approx(43_200)
    assert m.budget_spent(31_000, 43_200_000, 0.999) == pytest.approx(31_000 / 43_200) and m.budget_spent(0, 0, 0.999) == 0.0
    assert m.budget_spent(50_000, 43_200_000, 0.999) > 1
    assert m.burn_rate(12, 12_000, 0.999) == pytest.approx(1.0)
    assert m.burn_rate(1_800, 12_000, 0.999) == pytest.approx(150.0) and m.burn_rate(0, 0, 0.99) == 0.0
    assert m.days_to_exhaustion(150.0) == pytest.approx(0.2) and m.days_to_exhaustion(0) == float("inf") and m.days_to_exhaustion(2, 28) == 14


def test_slo_validation(load_exercise):
    m = load_exercise("ex03_slo")
    for slo in (0, 1, 1.5, -0.1):
        with pytest.raises(ValueError):
            m.error_budget(100, slo)
    with pytest.raises(ValueError):
        m.burn_rate(5, 3, 0.99)
    with pytest.raises(ValueError):
        m.burn_rate(-1, 3, 0.99)
    with pytest.raises(ValueError):
        m.error_budget(-1, 0.99)


def test_should_page_and_downtime(load_exercise):
    m = load_exercise("ex03_slo")
    assert m.should_page([(1_800, 12_000), (12_000, 720_000)], 0.999) is True
    assert m.should_page([(1_800, 12_000), (900, 720_000)], 0.999) is False                # pico curto, hora normal
    assert m.should_page([(1_800, 12_000)], 0.999, threshold=200) is False
    with pytest.raises(ValueError):
        m.should_page([], 0.999)
    assert m.allowed_downtime_minutes(0.999) == pytest.approx(43.2) and m.allowed_downtime_minutes(0.9999) == pytest.approx(4.32)
    assert m.allowed_downtime_minutes(0.99, 7) == pytest.approx(100.8)


# ---------- ex04 ----------
def test_request_context_nesting(load_exercise):
    m = load_exercise("ex04_correlation")
    assert m.get_request_id() == "-"
    with m.request_context("a"):
        assert m.get_request_id() == "a"
        with m.request_context("b"):
            assert m.get_request_id() == "b"
        assert m.get_request_id() == "a"
        with pytest.raises(RuntimeError):
            with m.request_context("c"):
                raise RuntimeError("falhou")
        assert m.get_request_id() == "a"
    assert m.get_request_id() == "-"


def test_filter_adds_request_id_to_logs(load_exercise):
    m = load_exercise("ex04_correlation")
    stream = io.StringIO()
    logger = logging.getLogger("cap68.test")
    logger.handlers.clear()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(request_id)s|%(message)s"))
    handler.addFilter(m.RequestIdFilter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.info("sem requisição")
    with m.request_context("req-9"):
        logger.info("dentro")
    assert stream.getvalue().splitlines() == ["-|sem requisição", "req-9|dentro"]


def test_fan_out_and_threads(load_exercise):
    m = load_exercise("ex04_correlation")
    assert asyncio.run(m.fan_out("req-7", 5)) == ["req-7"] * 5
    with m.request_context("req-8"):
        assert m.run_in_thread(m.get_request_id) == "req-8"
        assert m.run_in_thread(lambda a, b: (a + b, m.get_request_id()), 1, 2) == (3, "req-8")
    assert m.run_in_thread(m.get_request_id) == "-"
    seen = []
    with m.request_context("req-9"):
        t = threading.Thread(target=lambda: seen.append(m.get_request_id()))
        t.start()
        t.join()
    assert seen == ["-"]                                                   # thread comum NÃO herda o contexto


# ---------- ex05 ----------
GOOD = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"


def test_parse_and_format(load_exercise):
    m = load_exercise("ex05_traceparent")
    ctx = m.parse_traceparent(GOOD)
    assert (ctx.trace_id, ctx.span_id, ctx.sampled) == ("4bf92f3577b34da6a3ce929d0e0e4736", "00f067aa0ba902b7", True)
    assert m.format_traceparent(ctx) == GOOD
    assert m.parse_traceparent("  " + GOOD.replace("-01", "-00") + " ").sampled is False
    assert m.parse_traceparent(GOOD.replace("-01", "-03")).sampled is True
    assert m.format_traceparent(m.TraceContext("a" * 32, "b" * 16, False)).endswith("-00")


@pytest.mark.parametrize("bad", [
    "", "00-abc", GOOD + "-extra", GOOD.replace("00-", "01-", 1), "00-" + "0" * 32 + "-00f067aa0ba902b7-01",
    "00-4bf92f3577b34da6a3ce929d0e0e4736-" + "0" * 16 + "-01", "00-4BF92F3577B34DA6A3CE929D0E0E4736-00f067aa0ba902b7-01",
    "00-4bf92f3577b34da6a3ce929d0e0e47-00f067aa0ba902b7-01", "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-1",
    "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-zz",
])
def test_parse_rejects_invalid(load_exercise, bad):
    m = load_exercise("ex05_traceparent")
    with pytest.raises(ValueError):
        m.parse_traceparent(bad)


def test_child_of(load_exercise):
    m = load_exercise("ex05_traceparent")
    parent = m.parse_traceparent(GOOD)
    child = m.child_of(parent, random.Random(1))
    assert child.trace_id == parent.trace_id and child.sampled and child.span_id != parent.span_id
    assert len(child.span_id) == 16 and child.span_id == child.span_id.lower() and int(child.span_id, 16) != 0
    assert m.child_of(parent, random.Random(1)) == child                   # determinístico com a mesma semente
    class Zeros:
        calls = 0

        def getbits(self, n):
            self.calls += 1
            return 0 if self.calls == 1 else 255
    zeros = Zeros()
    fake = type("R", (), {"getrandbits": lambda self, n: zeros.getbits(n)})()
    assert m.child_of(parent, fake).span_id == "00000000000000ff" and zeros.calls == 2


def test_should_sample(load_exercise):
    m = load_exercise("ex05_traceparent")
    low = "0" * 16 + "0000000000000001"                                    # n pequeno: sempre dentro de qualquer amostra > 0
    high = "f" * 32
    assert m.should_sample(low, 0.01) is True and m.should_sample(high, 0.99) is False and m.should_sample(high, 1.0) is True
    assert m.should_sample(low, 0.0) is False
    rng = random.Random(3)
    ids = [f"{rng.getrandbits(128):032x}" for _ in range(20_000)]
    kept = sum(m.should_sample(i, 0.1) for i in ids)
    assert 1700 < kept < 2300
    assert all(m.should_sample(i, 0.1) == m.should_sample(i, 0.1) for i in ids[:100])
    with pytest.raises(ValueError):
        m.should_sample(low, 1.5)


# ---------- ex06 ----------
def test_health_ok_degraded_down(load_exercise):
    m = load_exercise("ex06_health")
    h = m.HealthChecker()
    assert h.run() == (200, {"status": "ok", "checks": {}})
    h.add("db", lambda: None)
    h.add("cache", lambda: None, critical=False)
    status, body = h.run()
    assert status == 200 and body["status"] == "ok" and body["checks"]["db"]["status"] == "ok" and isinstance(body["checks"]["db"]["ms"], int)
    h2 = m.HealthChecker()
    h2.add("db", lambda: None)
    h2.add("cache", lambda: (_ for _ in ()).throw(ConnectionError("cache fora")), critical=False)
    status, body = h2.run()
    assert status == 200 and body["status"] == "degraded" and body["checks"]["cache"] == {"status": "fail", "error": "cache fora", "ms": body["checks"]["cache"]["ms"]}
    h3 = m.HealthChecker()
    h3.add("db", lambda: (_ for _ in ()).throw(ConnectionError("banco fora")))
    status, body = h3.run()
    assert status == 503 and body["status"] == "down" and body["checks"]["db"]["error"] == "banco fora"
    with pytest.raises(ValueError):
        h3.add("db", lambda: None)


def test_health_timeout_does_not_block(load_exercise):
    m = load_exercise("ex06_health")
    h = m.HealthChecker()
    h.add("slow", lambda: time.sleep(2.0), critical=False, timeout=0.2)
    h.add("fast", lambda: time.sleep(0.01))
    start = time.perf_counter()
    status, body = h.run()
    elapsed = time.perf_counter() - start
    assert elapsed < 0.8, f"demorou {elapsed:.2f}s: o timeout não foi respeitado"
    assert status == 200 and body["status"] == "degraded" and body["checks"]["slow"]["status"] == "timeout" and body["checks"]["fast"]["status"] == "ok"
    h2 = m.HealthChecker()
    h2.add("slow", lambda: time.sleep(2.0), critical=True, timeout=0.2)
    start = time.perf_counter()
    assert h2.run()[0] == 503 and time.perf_counter() - start < 0.8


def test_health_runs_checks_concurrently(load_exercise):
    m = load_exercise("ex06_health")
    h = m.HealthChecker()
    for i in range(5):
        h.add(f"c{i}", lambda: time.sleep(0.2), timeout=1.0)
    start = time.perf_counter()
    status, body = h.run()
    assert time.perf_counter() - start < 0.6 and status == 200 and body["status"] == "ok"
