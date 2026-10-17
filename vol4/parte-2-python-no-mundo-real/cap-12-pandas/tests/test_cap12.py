import numpy as np
import pandas as pd
import pytest

from sample_data import make_dirty_orders


# ---------- ex01 ----------
def test_clean_orders_clean_part(load_exercise):
    m = load_exercise("ex01_clean_orders")
    clean, rejected = m.clean_orders(make_dirty_orders())
    assert list(clean.columns) == ["order_id", "customer", "date", "amount", "status"]
    assert clean["order_id"].tolist() == [1001, 1002, 1003]
    assert clean["customer"].tolist() == ["Ana Souza", "Bruno Lima", "Carla Dias"]
    assert clean["amount"].tolist() == [1250.5, 300.0, 89.9]
    assert clean["date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-03-01", "2026-03-01", "2026-03-04"]
    assert clean["status"].tolist() == ["paid", "paid", "pending"]
    assert str(clean["order_id"].dtype) == "Int64" and clean["amount"].dtype == "float64"
    assert pd.api.types.is_datetime64_any_dtype(clean["date"]) and clean.index.tolist() == [0, 1, 2]


def test_clean_orders_rejected_part(load_exercise):
    m = load_exercise("ex01_clean_orders")
    raw = make_dirty_orders()
    clean, rejected = m.clean_orders(raw)
    assert list(rejected.columns) == list(raw.columns) + ["reason"]
    assert rejected.index.tolist() == [4, 5, 6]
    assert rejected["reason"].tolist() == ["customer,date", "amount", "order_id"]
    assert len(clean) + len(rejected) == len(raw) - 1             # 1 duplicata exata descartada em silêncio


def test_clean_orders_does_not_touch_input_and_rejects_nonpositive(load_exercise):
    m = load_exercise("ex01_clean_orders")
    raw = pd.DataFrame({"Order ID": ["1", "2"], "Customer": ["a b", "c d"], "Date": ["2026-01-01", "2026-01-02"],
                        "Amount": ["0", "-5,50"], "Status": ["PAID", "paid"]})
    before = raw.copy()
    clean, rejected = m.clean_orders(raw)
    assert raw.equals(before) and len(clean) == 0 and rejected["reason"].tolist() == ["amount", "amount"]
    assert list(clean.columns) == ["order_id", "customer", "date", "amount", "status"]


# ---------- ex02 ----------
def sample_orders():
    return pd.DataFrame({
        "order_id": [1, 2, 3, 4, 5, 6, 7],
        "customer_id": [10, 10, 11, 12, 12, 12, 13],
        "product": ["a", "a", "b", "b", "c", "a", "c"],
        "qty": [1, 2, 3, 1, 1, 4, 9],
        "total": [10.0, 20.0, 90.0, 30.0, 5.0, 40.0, 999.0],
        "status": ["paid", "paid", "paid", "paid", "paid", "paid", "cancelled"],
        "date": pd.to_datetime(["2026-01-05", "2026-01-20", "2026-03-02", "2026-03-15", "2026-03-20", "2026-03-31", "2026-02-10"]),
    })


def test_product_report(load_exercise):
    m = load_exercise("ex02_sales_report")
    report = m.product_report(sample_orders())
    assert report.index.name == "product" and report.index.tolist() == ["b", "a", "c"]
    assert report.columns.tolist() == ["orders", "units", "revenue", "share"]
    assert report.loc["a"].tolist() == [3, 7, 70.0, pytest.approx(70 / 195)]
    assert report["share"].sum() == pytest.approx(1.0)
    assert report.loc["c", "revenue"] == 5.0                      # o cancelado (999) fica de fora


def test_monthly_revenue_fills_empty_months(load_exercise):
    m = load_exercise("ex02_sales_report")
    monthly = m.monthly_revenue(sample_orders())
    assert monthly.index.tolist() == list(pd.date_range("2026-01-01", "2026-03-01", freq="MS"))
    assert monthly.tolist() == [30.0, 0.0, 165.0] and monthly.dtype == "float64"
    assert monthly.index.freqstr == "MS"


def test_top_customers(load_exercise):
    m = load_exercise("ex02_sales_report")
    top = m.top_customers(sample_orders(), 2)
    assert top.columns.tolist() == ["customer_id", "revenue", "orders"]
    assert top.to_dict("list") == {"customer_id": [11, 12], "revenue": [90.0, 75.0], "orders": [1, 3]}
    assert top.index.tolist() == [0, 1]
    tie = pd.DataFrame({"order_id": [1, 2], "customer_id": [9, 3], "product": ["a", "a"], "qty": [1, 1],
                        "total": [5.0, 5.0], "status": ["paid", "paid"], "date": pd.to_datetime(["2026-01-01"] * 2)})
    assert m.top_customers(tie, 5)["customer_id"].tolist() == [3, 9]


# ---------- ex03 ----------
CUSTOMERS = pd.DataFrame({"customer_id": [1, 2, 3], "name": ["a", "b", "c"]})
ORDERS = pd.DataFrame({"order_id": [10, 11, 12, 13], "customer_id": [2, 9, 2, 1]})


def test_enrich(load_exercise):
    m = load_exercise("ex03_merge_checks")
    out = m.enrich(ORDERS, CUSTOMERS)
    assert out["order_id"].tolist() == [10, 11, 12, 13] and out.index.tolist() == [0, 1, 2, 3]
    assert out["name"].tolist()[0] == "b" and pd.isna(out["name"].tolist()[1]) and out["name"].tolist()[3] == "a"
    assert out.columns.tolist() == ["order_id", "customer_id", "name"]


def test_enrich_rejects_duplicate_customers(load_exercise):
    m = load_exercise("ex03_merge_checks")
    dup = pd.concat([CUSTOMERS, CUSTOMERS.iloc[[2, 0]], CUSTOMERS.iloc[[0]]])
    with pytest.raises(ValueError, match=r"clientes duplicados: \[1, 3\]"):
        m.enrich(ORDERS, dup)


def test_anti_joins(load_exercise):
    m = load_exercise("ex03_merge_checks")
    orphans = m.orphan_orders(ORDERS, CUSTOMERS)
    assert orphans["order_id"].tolist() == [11] and orphans.index.tolist() == [0]
    idle = m.customers_without_orders(ORDERS, CUSTOMERS)
    assert idle["customer_id"].tolist() == [3] and idle.columns.tolist() == ["customer_id", "name"]


# ---------- ex04 ----------
def daily_orders():
    return pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01 10:00", "2026-01-01 18:30", "2026-01-03 09:00", "2026-01-05 12:00"]),
        "total": [10.0, 5.0, 20.0, 30.0],
    })


def test_daily_revenue(load_exercise):
    m = load_exercise("ex04_time_features")
    series = m.daily_revenue(daily_orders())
    assert series.name == "revenue" and series.index.freqstr == "D"
    assert series.index.tolist() == list(pd.date_range("2026-01-01", "2026-01-05"))
    assert series.tolist() == [15.0, 0.0, 20.0, 0.0, 30.0]
    wide = m.daily_revenue(daily_orders(), start="2025-12-31", end="2026-01-06")
    assert len(wide) == 7 and wide.iloc[0] == 0.0 and wide.iloc[-1] == 0.0


def test_add_trend(load_exercise):
    m = load_exercise("ex04_time_features")
    series = m.daily_revenue(daily_orders())
    out = m.add_trend(series, window=2)
    assert out.columns.tolist() == ["revenue", "ma", "change", "growth"]
    assert out["ma"].isna().tolist() == [True, False, False, False, False]
    assert out["ma"].tolist()[1:] == [7.5, 10.0, 10.0, 15.0]
    assert out["change"].tolist()[1:] == [-15.0, 20.0, -20.0, 30.0]
    growth = out["growth"].tolist()
    assert np.isnan(growth[0]) and growth[1] == -100.0 and np.isnan(growth[2]) and growth[3] == -100.0 and np.isnan(growth[4])
    assert not np.isinf(out["growth"]).any()


def test_best_weekday(load_exercise):
    m = load_exercise("ex04_time_features")
    series = pd.Series([1.0, 9.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 5.0], index=pd.date_range("2026-03-02", periods=9))   # 02/03 é segunda
    assert m.best_weekday(series) == "Tuesday"
    assert m.best_weekday(pd.Series([1.0, 2.0, 3.0], index=pd.date_range("2026-03-06", periods=3))) == "Sunday"


# ---------- ex05 ----------
def diet_frame():
    n = 1000
    rng = np.random.default_rng(0)
    return pd.DataFrame({
        "small": rng.integers(0, 200, n),
        "signed": rng.integers(-100, 100, n),
        "big": rng.integers(0, 10**12, n),
        "city": rng.choice(["Recife", "Natal", "Salvador"], n),
        "uid": [f"user-{i}" for i in range(n)],
        "price": np.round(rng.integers(0, 1000, n) / 4, 2),
        "exact": rng.random(n),
        "flag": rng.random(n) > 0.5,
        "when": pd.Timestamp("2026-01-01") + pd.to_timedelta(rng.integers(0, 1000, n), unit="h"),
    })


def test_slim_dtypes(load_exercise):
    m = load_exercise("ex05_memory_diet")
    out = m.slim(diet_frame())
    assert out["small"].dtype == "uint8" and out["signed"].dtype == "int8" and out["big"].dtype == "uint64"
    assert out["city"].dtype == "category" and out["uid"].dtype != "category"
    assert out["price"].dtype == "float32" and out["exact"].dtype == "float64"
    assert out["flag"].dtype == bool and str(out["when"].dtype).startswith("datetime64")


def test_slim_keeps_values_and_input(load_exercise):
    m = load_exercise("ex05_memory_diet")
    df = diet_frame()
    before = df.copy()
    out = m.slim(df)
    assert df.equals(before) and out.columns.tolist() == df.columns.tolist() and out.index.equals(df.index)
    for name in ("small", "signed", "big", "city", "price", "exact", "flag"):
        assert (out[name].astype(df[name].dtype) == df[name]).all(), name


def test_slim_ratio_and_savings(load_exercise):
    m = load_exercise("ex05_memory_diet")
    df = diet_frame()
    out = m.slim(df)
    report = m.savings(df, out)
    assert set(report) == {"before", "after", "ratio"} and report["after"] < report["before"]
    assert report["ratio"] == round(report["before"] / report["after"], 2) and report["ratio"] > 1.2
    assert m.slim(df, max_unique_ratio=0.0)["city"].dtype != "category"


# ---------- ex06 ----------
def cohort_orders():
    return pd.DataFrame({
        "customer_id": [1, 1, 1, 2, 2, 3, 3, 4],
        "date": pd.to_datetime(["2026-01-05", "2026-01-20", "2026-03-02", "2026-01-30", "2026-02-10",
                                "2026-02-01", "2026-04-01", "2026-03-15"]),
    })


def test_first_purchase_month(load_exercise):
    m = load_exercise("ex06_cohorts")
    first = m.first_purchase_month(cohort_orders())
    assert first.name == "cohort" and first.index.tolist() == [1, 2, 3, 4]
    assert [str(p) for p in first] == ["2026-01", "2026-01", "2026-02", "2026-03"]


def test_retention_counts(load_exercise):
    m = load_exercise("ex06_cohorts")
    table = m.retention_counts(cohort_orders())
    assert table.index.name == "cohort" and table.columns.name == "months_since"
    assert [str(p) for p in table.index] == ["2026-01", "2026-02", "2026-03"]
    assert table.columns.tolist() == [0, 1, 2]
    assert table.values.tolist() == [[2, 1, 1], [1, 0, 1], [1, 0, 0]]
    assert all(np.issubdtype(t, np.integer) for t in table.dtypes)


def test_retention_rate(load_exercise):
    m = load_exercise("ex06_cohorts")
    rate = m.retention_rate(cohort_orders())
    assert rate[0].tolist() == [1.0, 1.0, 1.0]
    assert rate.values.tolist() == [[1.0, 0.5, 0.5], [1.0, 0.0, 1.0], [1.0, 0.0, 0.0]]
