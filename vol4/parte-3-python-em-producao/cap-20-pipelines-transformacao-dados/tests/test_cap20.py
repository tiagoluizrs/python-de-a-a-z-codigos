import itertools
import random
import sqlite3

import pytest


# ---------- ex01 ----------
HEADER = "event_id,user_id,product,qty,price\n"


def test_parse_line(load_exercise):
    m = load_exercise("ex01_etl_stream")
    assert m.parse_line("1, 7 , Caneta ,3,2.50\n") == {"event_id": 1, "user_id": 7, "product": "caneta", "qty": 3, "price": 2.5, "total": 7.5}
    for line, reason in [("1,2,x", "colunas"), ("1,2,x,3,4,5", "colunas"), ("1, ,caneta,1,1", "user_id vazio"), ("a,2,x,1,1", "número inválido"),
                         ("1,2,x,1.5,1", "número inválido"), ("1,2,x,1,abc", "número inválido"), ("1,2,x,0,1", "quantidade não positiva"),
                         ("1,2,x,-3,1", "quantidade não positiva"), ("1,2,x,1,-0.5", "preço negativo"), ("1,,x,abc,1", "user_id vazio")]:
        with pytest.raises(m.Rejected) as info:
            m.parse_line(line)
        assert str(info.value) == reason, line


def test_transform_is_lazy_and_collects_rejects(load_exercise):
    m = load_exercise("ex01_etl_stream")
    consumed = []

    def source():
        lines = [HEADER, "1,10,caneta,2,2.5\n", "\n", "2,,mouse,1,45\n", "3,11,teclado,0,89.9\n", "1,12,caneta,1,2.5\n", "4,13,Monitor,1,799\n", "  \n"]
        for line in lines:
            consumed.append(line)
            yield line

    rejects = []
    gen = m.transform(source(), rejects)
    first = next(gen)
    assert first["event_id"] == 1 and first["total"] == 5.0
    assert len(consumed) == 2 and rejects == []                                  # só leu o cabeçalho e a 1ª linha: é preguiçoso
    rest = list(gen)
    assert [r["event_id"] for r in rest] == [4] and rest[0]["product"] == "monitor"
    assert rejects == [(4, "user_id vazio"), (5, "quantidade não positiva"), (6, "event_id duplicado")]      # linha em branco (3 e 8) ignorada
    assert len(consumed) == 8


def test_transform_without_header_and_big_input(load_exercise):
    m = load_exercise("ex01_etl_stream")
    rejects = []
    good = list(m.transform(["1,1,a,1,1", "2,1,b,1,1"], rejects, skip_header=False))
    assert [g["event_id"] for g in good] == [1, 2] and rejects == []
    big = (f"{i},{i},p,1,1.0\n" for i in range(1, 200_001))
    count = sum(1 for _ in m.transform(itertools.chain([HEADER], big), []))
    assert count == 200_000


def test_batched_and_summarize(load_exercise):
    m = load_exercise("ex01_etl_stream")
    assert list(m.batched(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]] and list(m.batched([], 3)) == []
    pulled = []

    def counting():
        for i in range(100):
            pulled.append(i)
            yield i

    it = m.batched(counting(), 10)
    assert next(it) == list(range(10)) and len(pulled) == 10                     # não puxou além do necessário
    with pytest.raises(ValueError):
        next(m.batched([1], 0))
    rejects = [(2, "colunas"), (5, "user_id vazio"), (7, "colunas"), (9, "preço negativo"), (11, "user_id vazio"), (12, "x")]
    summary = m.summarize(10, rejects)
    assert summary == {"loaded": 10, "rejected": 6, "reasons": {"colunas": 2, "user_id vazio": 2, "preço negativo": 1, "x": 1}} and list(summary["reasons"]) == ["colunas", "user_id vazio", "preço negativo", "x"]


# ---------- ex02 ----------
def row(order_id, day="2026-03-01", total=10.0, updated="2026-03-01T10:00"):
    return {"order_id": order_id, "day": day, "total": total, "updated_at": updated}


def test_upsert_semantics(load_exercise):
    m = load_exercise("ex02_upsert")
    db = m.make_db()
    assert m.upsert(db, [row(1), row(2, total=20.0)]) == {"inserted": 2, "updated": 0, "ignored": 0}
    assert m.upsert(db, [row(1), row(2, total=20.0)]) == {"inserted": 0, "updated": 0, "ignored": 2}            # reexecução: estável
    assert m.upsert(db, [row(2, total=80.0, updated="2026-03-02T09:00")]) == {"inserted": 0, "updated": 1, "ignored": 0}
    assert m.upsert(db, [row(2, total=999.0, updated="2026-03-01T08:00")]) == {"inserted": 0, "updated": 0, "ignored": 1}
    assert db.execute("select total from sales where order_id = 2").fetchone()[0] == 80.0
    assert m.upsert(db, [row(3), row(3, total=5.0, updated="2026-03-01T11:00"), row(3, total=6.0, updated="2026-03-01T11:00")]) == {"inserted": 1, "updated": 1, "ignored": 1}
    assert db.execute("select total from sales where order_id = 3").fetchone()[0] == 5.0


def test_upsert_is_atomic(load_exercise):
    m = load_exercise("ex02_upsert")
    db = m.make_db()
    with pytest.raises(sqlite3.IntegrityError):
        m.upsert(db, [row(1), row(2, total=None)])
    assert db.execute("select count(*) from sales").fetchone()[0] == 0


def test_replace_partition(load_exercise):
    m = load_exercise("ex02_upsert")
    db = m.make_db()
    m.upsert(db, [row(1), row(2, total=20.0), row(3, day="2026-03-02", total=5.0)])
    assert m.replace_partition(db, "2026-03-01", [row(10, total=1.0), row(11, total=2.0), row(12, total=3.0)]) == 3
    assert m.totals_by_day(db) == {"2026-03-01": (3, 6.0), "2026-03-02": (1, 5.0)}
    assert m.replace_partition(db, "2026-03-01", [row(10, total=1.0)]) == 1 and m.totals_by_day(db)["2026-03-01"] == (1, 1.0)
    before = m.totals_by_day(db)
    with pytest.raises(ValueError):
        m.replace_partition(db, "2026-03-01", [row(20), row(21, day="2026-03-05")])
    with pytest.raises(sqlite3.IntegrityError):
        m.replace_partition(db, "2026-03-01", [row(30), row(30)])                  # falha no meio: as linhas antigas voltam
    assert m.totals_by_day(db) == before
    assert m.replace_partition(db, "2026-03-09", []) == 0


# ---------- ex03 ----------
def test_execution_order_and_errors(load_exercise):
    m = load_exercise("ex03_dag")
    t = m.Task
    tasks = [t("report", lambda x: x, ["join"]), t("join", lambda a, b: a + b, ["clean_b", "clean_a"]), t("clean_b", lambda x: x, ["b"]),
             t("clean_a", lambda x: x, ["a"]), t("b", lambda: 1), t("a", lambda: 1)]
    assert m.execution_order(tasks) == ["a", "b", "clean_a", "clean_b", "join", "report"]
    with pytest.raises(ValueError, match="x depende de y, que não existe"):
        m.execution_order([t("x", lambda: 1, ["y"])])
    with pytest.raises(ValueError, match="ciclo: a -> c -> b -> a"):
        m.execution_order([t("c", lambda x: x, ["b"]), t("a", lambda x: x, ["c"]), t("b", lambda x: x, ["a"]), t("z", lambda: 1)])
    with pytest.raises(ValueError):
        m.execution_order([t("a", lambda: 1), t("a", lambda: 2)])


def test_run_cache_and_invalidation(load_exercise):
    m = load_exercise("ex03_dag")
    calls = []

    def src_a():
        calls.append("a")
        return [1, 2]

    def src_b():
        calls.append("b")
        return [10]

    def total(a, b):
        calls.append("total")
        return sum(a) + sum(b)

    def build(version_a="1"):
        return [m.Task("a", src_a, version=version_a), m.Task("b", src_b), m.Task("total", total, ["a", "b"])]

    cache = {}
    first = m.run(build(), cache)
    assert first["outputs"]["total"] == 13 and first["log"] == [("a", "ok"), ("b", "ok"), ("total", "ok")] and calls == ["a", "b", "total"]
    calls.clear()
    second = m.run(build(), cache)
    assert second["log"] == [("a", "cache"), ("b", "cache"), ("total", "cache")] and calls == []
    third = m.run(build("2"), cache)                                                # o código de A mudou: A e o que depende dele refazem
    assert third["log"] == [("a", "ok"), ("b", "cache"), ("total", "ok")] and calls == ["a", "total"]


def test_run_failures_skip_dependents_and_resume(load_exercise):
    m = load_exercise("ex03_dag")
    state = {"broken": True, "attempts": 0}

    def flaky():
        state["attempts"] += 1
        if state["attempts"] < 3:
            raise ConnectionError("fora")
        return 5

    def report(x):
        if state["broken"]:
            raise ValueError("bug")
        return x * 2

    def tasks():
        return [m.Task("flaky", flaky, retries=2), m.Task("ok", lambda: 1), m.Task("report", report, ["flaky"]), m.Task("final", lambda r, o: r + o, ["report", "ok"])]

    cache = {}
    result = m.run(tasks(), cache)
    assert state["attempts"] == 3 and result["failed"] == ["report"] and result["skipped"] == ["final"]
    assert dict(result["log"]) == {"flaky": "ok", "ok": "ok", "report": "falhou", "final": "pulada"} and "report" not in result["outputs"]
    state["broken"] = False
    state["attempts"] = 0
    resumed = m.run(tasks(), cache)
    assert dict(resumed["log"]) == {"flaky": "cache", "ok": "cache", "report": "ok", "final": "ok"} and state["attempts"] == 0 and resumed["outputs"]["final"] == 11
    only_fail = m.run([m.Task("bad", lambda: 1 / 0, retries=1), m.Task("fine", lambda: 2)], {})
    assert only_fail["failed"] == ["bad"] and only_fail["outputs"] == {"fine": 2}


# ---------- ex04 ----------
class Source:
    def __init__(self, rows):
        self.rows, self.calls = rows, []

    def fetch(self, since):
        self.calls.append(since)
        return [dict(r) for r in self.rows if r["updated_at"] > since]


def test_incremental_basic(load_exercise):
    m = load_exercise("ex04_watermark")
    src = Source([{"id": i, "updated_at": f"2026-03-01T{8 + i:02d}:00"} for i in range(1, 4)])
    state = {}
    ex = m.IncrementalExtractor(state, src.fetch)
    first = ex.run()
    assert [r["id"] for r in first["new"]] == [1, 2, 3] and first["watermark"] == "2026-03-01T11:00" and first["fetched"] == 3 and src.calls == ["1970-01-01T00:00"]
    again = ex.run()
    assert again == {"new": [], "watermark": "2026-03-01T11:00", "fetched": 0} and src.calls[-1] == "2026-03-01T11:00"
    src.rows.append({"id": 4, "updated_at": "2026-03-02T09:00"})
    src.rows[0] = {"id": 1, "updated_at": "2026-03-02T10:00"}
    third = ex.run()
    assert [(r["id"], r["updated_at"]) for r in third["new"]] == [(4, "2026-03-02T09:00"), (1, "2026-03-02T10:00")] and third["watermark"] == "2026-03-02T10:00"


def test_incremental_late_arrivals_and_overlap(load_exercise):
    m = load_exercise("ex04_watermark")
    src = Source([{"id": 1, "updated_at": "2026-03-01T12:00"}])
    plain_state, overlap_state = {}, {}
    plain, overlap = m.IncrementalExtractor(plain_state, src.fetch), m.IncrementalExtractor(overlap_state, src.fetch, overlap_minutes=60)
    plain.run()
    overlap.run()
    src.rows.append({"id": 2, "updated_at": "2026-03-01T11:30"})                  # chegou DEPOIS, com updated_at ANTES da marca d'água
    assert plain.run()["new"] == []                                                # sem sobreposição: perdido
    got = overlap.run()
    assert [r["id"] for r in got["new"]] == [2] and got["fetched"] == 2 and got["watermark"] == "2026-03-01T12:00"
    assert overlap.run()["new"] == []                                              # e não volta a ser entregue (idempotente)


def test_incremental_state_untouched_on_error_and_memory(load_exercise):
    m = load_exercise("ex04_watermark")

    def boom(since):
        raise ConnectionError("origem fora")

    state = {"watermark": "2026-03-01T10:00", "seen": {(1, "2026-03-01T10:00")}}
    snapshot = {"watermark": state["watermark"], "seen": set(state["seen"])}
    with pytest.raises(ConnectionError):
        m.IncrementalExtractor(state, boom, overlap_minutes=30).run()
    assert state == snapshot
    rows = [{"id": i, "updated_at": m.shift_minutes("2026-03-01T00:00", i * 10)} for i in range(100)]
    src = Source(rows)
    st = {}
    ex = m.IncrementalExtractor(st, src.fetch, overlap_minutes=60)
    ex.run()
    assert len(st["seen"]) <= 7 and st["watermark"] == rows[-1]["updated_at"]          # só a janela de sobreposição fica na memória
    assert m.shift_minutes("2026-03-01T23:50", 20) == "2026-03-02T00:10" and m.shift_minutes("2026-03-01T00:10", -20) == "2026-02-28T23:50"


# ---------- ex05 ----------
ROWS = [
    {"id": 1, "qty": 5, "country": "BR", "name": "ana"},
    {"id": 2, "qty": 0, "country": "BR", "name": " "},
    {"id": 3, "qty": 500, "country": "XX", "name": "bia"},
    {"id": 3, "qty": 7, "country": "AR", "name": None},
    {"id": 4, "qty": "9", "country": "BR", "name": "dan"},
    {"id": 5, "qty": True, "country": "AR", "name": "eva"},
]


def test_check_builders(load_exercise):
    m = load_exercise("ex05_quality")
    assert m.not_null("name").name == "name não nulo" and [m.not_null("name").predicate(r) for r in ROWS] == [True, False, True, False, True, True]
    check = m.in_range("qty", 1, 100)
    assert check.name == "qty em [1, 100]" and [check.predicate(r) for r in ROWS] == [True, False, False, True, False, False]
    assert m.in_range("missing", 0, 1).predicate({}) is False
    assert m.one_of("country", {"BR", "AR"}).name == "country permitido" and [m.one_of("country", {"BR", "AR"}).predicate(r) for r in ROWS][2] is False
    assert [r["id"] for r in m.unique_rows(ROWS, "id")] == [3, 3]


def test_run_checks_report_and_gate(load_exercise):
    m = load_exercise("ex05_quality")
    checks = [m.not_null("name"), m.in_range("qty", 1, 100), m.one_of("country", {"BR", "AR"})]
    from dataclasses import replace
    checks[2] = replace(checks[2], severity="warn")
    checks[0] = replace(checks[0], tolerance=0.4)
    report = m.run_checks(ROWS, checks, unique=("id",))
    names = [c["name"] for c in report["checks"]]
    assert report["total"] == 6 and names == ["name não nulo", "qty em [1, 100]", "country permitido", "id único"]
    by = {c["name"]: c for c in report["checks"]}
    assert by["name não nulo"] == {"name": "name não nulo", "bad": 2, "ratio": 0.3333, "tolerance": 0.4, "status": "ok"}
    assert by["qty em [1, 100]"]["bad"] == 4 and by["qty em [1, 100]"]["status"] == "fail"
    assert by["country permitido"]["status"] == "warn" and by["id único"]["bad"] == 2 and by["id único"]["status"] == "fail"
    with pytest.raises(m.DataQualityError) as info:
        m.gate(report)
    assert str(info.value) == "qty em [1, 100]: 66.67% > 0.00%; id único: 33.33% > 0.00%"
    m.gate(m.run_checks(ROWS, [checks[0], checks[2]]))                                           # só ok e warn: passa
    assert m.run_checks([], checks)["checks"][0]["ratio"] == 0.0


def test_predicate_exceptions_and_split(load_exercise):
    m = load_exercise("ex05_quality")
    boom = m.Check("explode", lambda r: r["inexistente"] > 1)
    assert m.run_checks([{"a": 1}], [boom])["checks"][0]["bad"] == 1
    warn = m.Check("aviso", lambda r: False, severity="warn")
    good, bad = m.split(ROWS, [m.not_null("name"), m.in_range("qty", 1, 100), warn])
    assert [r["id"] for r in good] == [1] and [r["id"] for r in bad] == [2, 3, 3, 4, 5]
    assert m.split(ROWS, [warn]) == (ROWS, [])


# ---------- ex06 ----------
def test_windows_close_with_watermark(load_exercise):
    m = load_exercise("ex06_windows")
    w = m.TumblingWindows(10, lateness=5)
    assert w.add(1, "a") == [] and w.add(12, "a") == [] and w.add(9, "b") == []                 # marca 7, depois 7 (max 12 - 5)
    assert w.open_windows == 2
    closed = w.add(15, "a")                                                                     # marca 10: a janela [0,10) fecha
    assert closed == [(0, "a", 1.0), (0, "b", 1.0)] and w.open_windows == 1
    assert w.add(8, "a") == [] and w.dropped == 1                                               # janela [0,10) já fechou: descartado
    assert w.add(10, "a", 2.5) == [] and w.add(25, "a") == [(10, "a", 4.5)] and w.dropped == 1  # marca 20: fecha [10,20)
    assert w.flush() == [(20, "a", 1.0)] and w.open_windows == 0 and w.flush() == []


def test_windows_equal_to_batch_with_enough_lateness(load_exercise):
    m = load_exercise("ex06_windows")
    rng = random.Random(1)
    events = [(i // 5, rng.choice("xyz"), 1.0) for i in range(5000)]
    arrival = sorted(events, key=lambda e: e[0] + rng.uniform(0, 30))
    truth = m.batch_totals(arrival, 60)
    assert sum(truth.values()) == 5000 and all(start % 60 == 0 for start, _ in truth)
    w = m.TumblingWindows(60, lateness=30)
    result = {}
    for ts, key, value in arrival:
        for start, k, total in w.add(ts, key, value):
            result[(start, k)] = total
    for start, k, total in w.flush():
        result[(start, k)] = total
    assert result == truth and w.dropped == 0
    strict = m.TumblingWindows(60, lateness=0)
    for ts, key, value in arrival:
        strict.add(ts, key, value)
    assert strict.dropped > 0


def test_windows_validation_and_memory(load_exercise):
    m = load_exercise("ex06_windows")
    for args in ((0, 0), (10, -1)):
        with pytest.raises(ValueError):
            m.TumblingWindows(*args)
    with pytest.raises(ValueError):
        m.TumblingWindows(10).add(-1, "a")
    w = m.TumblingWindows(10, lateness=10)
    peak = 0
    for ts in range(0, 100_000, 3):
        w.add(ts, "k")
        peak = max(peak, w.open_windows)
    assert peak <= 3                                                                        # a memória é limitada pela tolerância, não pelo volume
