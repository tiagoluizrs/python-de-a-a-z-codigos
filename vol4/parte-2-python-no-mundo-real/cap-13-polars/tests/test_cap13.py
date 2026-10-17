from datetime import date, datetime

import polars as pl
import pytest
from polars.testing import assert_frame_equal


# ---------- ex01 ----------
def sales():
    return pl.DataFrame({
        "qty": [1, 2, 10, 3],
        "unit_price": [50.0, 30.0, 150.0, 400.0],
        "date": [datetime(2026, 3, 7, 10), datetime(2026, 3, 8, 12), datetime(2026, 3, 9, 8), datetime(2026, 4, 30, 23)],
        "status": ["paid", "pending", "paid", "paid"],
    })


def test_add_features(load_exercise):
    m = load_exercise("ex01_features")
    df = sales()
    before = df.clone()
    out = m.add_features(df)
    assert out.columns == ["qty", "unit_price", "date", "status", "total", "tier", "weekday", "is_weekend", "month", "paid_total"]
    assert out["total"].to_list() == [50.0, 60.0, 1500.0, 1200.0]
    assert out["tier"].to_list() == ["baixo", "baixo", "alto", "alto"]
    assert out["weekday"].to_list() == ["Saturday", "Sunday", "Monday", "Thursday"]
    assert out["is_weekend"].to_list() == [True, True, False, False]
    assert out["month"].to_list() == [date(2026, 3, 1)] * 3 + [date(2026, 4, 1)] and out.schema["month"] == pl.Date
    assert out["paid_total"].to_list() == [50.0, 0.0, 1500.0, 1200.0]
    assert_frame_equal(df, before)                                 # o argumento não foi alterado


def test_tier_counts(load_exercise):
    m = load_exercise("ex01_features")
    df = pl.concat([sales(), sales().with_columns(qty=pl.lit(2, dtype=pl.Int64)).head(1)])    # +1 linha de total 100 -> médio
    counts = m.tier_counts(df)
    assert counts == {"alto": 2, "baixo": 2, "médio": 1} and list(counts) == ["alto", "baixo", "médio"]


# ---------- ex02 ----------
def orders():
    return pl.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 6, 7],
        "customer_id": [1, 1, 1, 2, 2, 3, 3],
        "date": [datetime(2026, 1, d) for d in (5, 1, 9, 2, 3, 4, 8)],
        "product": ["a", "b", "b", "a", "a", "c", "c"],
        "total": [10.0, 30.0, 25.0, 40.0, 40.0, 500.0, 5.0],
        "status": ["paid", "paid", "paid", "paid", "cancelled", "paid", "paid"],
    })


def test_customer_report(load_exercise):
    m = load_exercise("ex02_customer_report")
    report = m.customer_report(orders())
    assert report.columns == ["customer_id", "orders", "revenue", "first_order", "last_order", "top_product"]
    assert report["customer_id"].to_list() == [3, 2, 1] or report["customer_id"].to_list() == [3, 1, 2]
    rows = {r["customer_id"]: r for r in report.to_dicts()}
    assert rows[1]["orders"] == 3 and rows[1]["revenue"] == 65.0 and rows[1]["top_product"] == "b"
    assert rows[1]["first_order"] == datetime(2026, 1, 1) and rows[1]["last_order"] == datetime(2026, 1, 9)
    assert rows[2]["orders"] == 1 and rows[2]["revenue"] == 40.0 and rows[2]["top_product"] == "a"   # o cancelado fica de fora
    assert report.schema["orders"] == pl.UInt32
    assert report["customer_id"].to_list() == [3, 1, 2]


def test_customer_report_tie_goes_alphabetical(load_exercise):
    m = load_exercise("ex02_customer_report")
    df = pl.DataFrame({"order_id": [1, 2], "customer_id": [7, 7], "date": [datetime(2026, 1, 1)] * 2,
                       "product": ["z", "b"], "total": [10.0, 10.0], "status": ["paid", "paid"]})
    assert m.customer_report(df)["top_product"].to_list() == ["b"]


def test_share_within_product(load_exercise):
    m = load_exercise("ex02_customer_report")
    out = m.share_within_product(orders())
    assert out.columns == orders().columns + ["share", "rank"]
    assert out["order_id"].to_list() == [1, 2, 3, 4, 5, 6, 7]
    assert out["share"].to_list()[0] == pytest.approx(10 / 90)            # produto a: 10 + 40 + 40 (todos os status)
    assert out["rank"].to_list() == [3, 1, 2, 1, 2, 1, 2]
    assert out.group_by("product").agg(pl.col("share").sum())["share"].to_list() == pytest.approx([1.0] * 3)


# ---------- ex03 ----------
@pytest.fixture
def parquet(tmp_path):
    df = pl.DataFrame({
        "order_id": range(1, 7),
        "date": [datetime(2026, 1, 5), datetime(2026, 1, 20), datetime(2026, 3, 2), datetime(2026, 3, 9), datetime(2026, 3, 9), datetime(2026, 1, 1)],
        "product": list("abcabc"), "qty": [1] * 6, "total": [10.0, 20.0, 5.0, 7.0, 100.0, 1.0],
        "status": ["paid", "paid", "paid", "pending", "cancelled", "paid"],
        "extra1": ["x"] * 6, "extra2": [1.5] * 6,
    })
    path = tmp_path / "orders.parquet"
    df.write_parquet(path)
    return path


def test_query_is_lazy_and_correct(load_exercise, parquet):
    m = load_exercise("ex03_lazy_pipeline")
    query = m.monthly_revenue_query(parquet)
    assert isinstance(query, pl.LazyFrame)
    out = query.collect()
    assert out.columns == ["month", "revenue", "orders"]
    assert out.to_dicts() == [{"month": date(2026, 1, 1), "revenue": 31.0, "orders": 3}, {"month": date(2026, 3, 1), "revenue": 5.0, "orders": 1}]
    assert out.schema["month"] == pl.Date
    assert_frame_equal(m.run(parquet), out)


def test_plan_pushes_filter_into_scan(load_exercise, parquet):
    m = load_exercise("ex03_lazy_pipeline")
    plan = m.explain_text(parquet)
    assert "SCAN" in plan and "SELECTION" in plan                          # o filtro foi empurrado para a leitura
    assert "PROJECT */8 COLUMNS" not in plan                               # e nem todas as colunas são lidas


# ---------- ex04 ----------
def keyed():
    return pl.DataFrame({"key": ["b", "a", "c", "a", "b", "z"] * 200, "value": list(range(1200))})


def test_totals_by_key_is_deterministic(load_exercise):
    m = load_exercise("ex04_deterministic")
    runs = [m.totals_by_key(keyed()) for _ in range(5)]
    assert all(r["key"].to_list() == ["a", "b", "c", "z"] for r in runs)
    assert runs[0]["total"].to_list() == [sum(range(1, 1200, 6)) + sum(range(3, 1200, 6)), sum(range(0, 1200, 6)) + sum(range(4, 1200, 6)), sum(range(2, 1200, 6)), sum(range(5, 1200, 6))]
    assert runs[0].columns == ["key", "total"]


def test_first_seen_order(load_exercise):
    m = load_exercise("ex04_deterministic")
    for _ in range(5):
        assert m.first_seen_order(keyed())["key"].to_list() == ["b", "a", "c", "z"]


def test_attach_names_keeps_order(load_exercise):
    m = load_exercise("ex04_deterministic")
    df = pl.DataFrame({"key": [f"k{i % 700}" for i in range(5000)], "n": list(range(5000))})
    names = pl.DataFrame({"key": [f"k{i}" for i in range(0, 700, 2)], "name": [f"name{i}" for i in range(0, 700, 2)]})
    for _ in range(3):
        out = m.attach_names(df, names)
        assert out["n"].to_list() == list(range(5000)) and out.height == 5000
        assert out["name"].to_list()[0] == "name0" and out["name"].to_list()[1] is None
    with pytest.raises(ValueError):
        m.attach_names(df, pl.concat([names, names.head(1)]))


# ---------- ex05 ----------
def events():
    t = lambda h, mi: datetime(2026, 1, 1, h, mi)
    return pl.DataFrame({
        "user": ["b", "a", "a", "a", "b", "a", "a"],
        "ts": [t(9, 5), t(10, 40), t(10, 0), t(10, 10), t(9, 0), t(12, 0), t(12, 10)],
    })


def test_sessionize(load_exercise):
    m = load_exercise("ex05_sessions")
    out = m.sessionize(events())
    assert out.columns == ["user", "ts", "session"]
    assert out["user"].to_list() == ["a"] * 5 + ["b"] * 2
    assert out["session"].to_list() == [1, 1, 1, 2, 2, 1, 1]               # 10:10 -> 10:40 = 30 min exatos: mesma sessão


def test_sessionize_gap_parameter(load_exercise):
    m = load_exercise("ex05_sessions")
    assert m.sessionize(events(), 29)["session"].to_list() == [1, 1, 2, 3, 3, 1, 1]
    assert m.sessionize(events(), 200)["session"].to_list() == [1, 1, 1, 1, 1, 1, 1]


def test_session_summary(load_exercise):
    m = load_exercise("ex05_sessions")
    out = m.session_summary(events())
    assert out.columns == ["user", "session", "start", "end", "events", "minutes"]
    assert out["user"].to_list() == ["a", "a", "b"] and out["session"].to_list() == [1, 2, 1]
    assert out["events"].to_list() == [3, 2, 2] and out.schema["events"] == pl.UInt32
    assert out["minutes"].to_list() == [40.0, 10.0, 5.0] and out.schema["minutes"] == pl.Float64
    assert out["start"].to_list()[0] == datetime(2026, 1, 1, 10, 0) and out["end"].to_list()[1] == datetime(2026, 1, 1, 12, 10)


# ---------- ex06 ----------
def test_top_n(load_exercise):
    m = load_exercise("ex06_port_pandas")
    df = pl.DataFrame({"g": ["b", "a", "a", "b", "a", "b", "c"], "v": [5, 9, 9, 7, 1, 7, 3], "tag": list("pqrstuv")})
    out = m.top_n(df, "g", "v", 2)
    assert out.columns == ["g", "v", "tag"]
    assert out["g"].to_list() == ["a", "a", "b", "b", "c"]
    assert out["tag"].to_list() == ["q", "r", "s", "u", "v"]                # empate de 9 (q, r) e de 7 (s, u): ordem original
    assert m.top_n(df, "g", "v", 10).height == 7


def test_growth_by_group(load_exercise):
    m = load_exercise("ex06_port_pandas")
    df = pl.DataFrame({"g": ["a", "b", "a", "a", "b", "a"], "day": [3, 1, 1, 2, 2, 4], "v": [150.0, 10.0, 100.0, 0.0, 20.0, 300.0]})
    out = m.growth_by_group(df, "g", "day", "v")
    assert out.columns == ["g", "day", "v", "growth"]
    assert out["g"].to_list() == ["a", "a", "a", "a", "b", "b"] and out["day"].to_list() == [1, 2, 3, 4, 1, 2]
    growth = out["growth"].to_list()
    assert growth[0] is None and growth[1] == -100.0 and growth[2] is None and growth[3] == 100.0
    assert growth[4] is None and growth[5] == 100.0


def test_to_pandas_safely(load_exercise):
    m = load_exercise("ex06_port_pandas")
    pdf, report = m.to_pandas_safely(pl.DataFrame({"a": [1, 2], "b": ["x", "y"], "c": [1.5, 2.5]}))
    assert list(pdf.columns) == ["a", "b", "c"] and report["a"] == "int64" and report["c"] == "float64"
    nested = pl.DataFrame({"a": [1], "l": [[1, 2]], "s": [{"x": 1}]})
    with pytest.raises(TypeError, match=r"colunas aninhadas: \['l', 's'\]"):
        m.to_pandas_safely(nested)
