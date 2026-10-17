"""A MESMA transformação em cinco motores: tempo e pico de memória (cada motor em um processo separado)."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent

CHILD = r'''
import csv, json, sqlite3, sys, time
from collections import defaultdict
from pathlib import Path

import psutil

engine, path = sys.argv[1], sys.argv[2]
FIX = {"br": "BR", "Brasil": "BR"}


def python_dict():
    revenue = defaultdict(float)
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for event_id, user, ts, product, qty, price, country in reader:
            try:
                q, p = int(qty), float(price)
            except ValueError:
                continue
            if q <= 0 or not user:
                continue
            revenue[FIX.get(country, country)] += q * p
    return {k: round(v, 2) for k, v in sorted(revenue.items())}


def pandas_default():
    import pandas as pd
    df = pd.read_csv(path)
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df[(df["qty"] > 0) & df["price"].notna() & df["user_id"].notna()]
    df["country"] = df["country"].replace(FIX)
    out = (df["qty"] * df["price"]).groupby(df["country"]).sum().round(2)
    return {k: float(v) for k, v in sorted(out.items())}


def pandas_arrow():
    import pandas as pd
    df = pd.read_csv(path, engine="pyarrow", usecols=["user_id", "qty", "price", "country"], dtype_backend="pyarrow")
    df["qty"] = pd.to_numeric(df["qty"], errors="coerce")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df[(df["qty"] > 0) & df["price"].notna() & df["user_id"].notna()]
    df["country"] = df["country"].replace(FIX)
    out = (df["qty"] * df["price"]).groupby(df["country"]).sum().round(2)
    return {k: float(v) for k, v in sorted(out.items())}


def polars_eager():
    import polars as pl
    df = pl.read_csv(path, schema_overrides={"qty": pl.String, "price": pl.String}, columns=["user_id", "qty", "price", "country"])
    out = (
        df.with_columns(qty=pl.col("qty").cast(pl.Int64, strict=False), price=pl.col("price").cast(pl.Float64, strict=False))
        .filter((pl.col("qty") > 0) & pl.col("price").is_not_null() & pl.col("user_id").is_not_null())
        .with_columns(country=pl.col("country").replace(FIX))
        .group_by("country").agg(revenue=(pl.col("qty") * pl.col("price")).sum().round(2)).sort("country")
    )
    return dict(zip(out["country"].to_list(), out["revenue"].to_list()))


def polars_lazy():
    import polars as pl
    out = (
        pl.scan_csv(path, schema_overrides={"qty": pl.String, "price": pl.String})
        .select("user_id", "qty", "price", "country")
        .with_columns(qty=pl.col("qty").cast(pl.Int64, strict=False), price=pl.col("price").cast(pl.Float64, strict=False))
        .filter((pl.col("qty") > 0) & pl.col("price").is_not_null() & pl.col("user_id").is_not_null())
        .with_columns(country=pl.col("country").replace(FIX))
        .group_by("country").agg(revenue=(pl.col("qty") * pl.col("price")).sum().round(2)).sort("country")
        .collect(engine="streaming")
    )
    return dict(zip(out["country"].to_list(), out["revenue"].to_list()))


def sqlite_sql():
    db = sqlite3.connect(":memory:")
    db.execute("create table t (event_id text, user_id text, ts text, product text, qty text, price text, country text)")
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        db.executemany("insert into t values (?, ?, ?, ?, ?, ?, ?)", reader)
    rows = db.execute("""
        select case country when 'br' then 'BR' when 'Brasil' then 'BR' else country end as c,
               round(sum(cast(qty as integer) * cast(price as real)), 2)
        from t
        where cast(qty as integer) > 0 and cast(price as real) > 0 and user_id <> ''
        group by c order by c""").fetchall()
    return dict(rows)


start = time.perf_counter()
result = globals()[engine]()
seconds = time.perf_counter() - start
proc = psutil.Process()
info = proc.memory_info()
peak = getattr(info, "peak_wset", None) or getattr(info, "rss")
print(json.dumps({"seconds": seconds, "peak_mb": peak / 1e6, "result": result}))
'''


def main():
    sys.path.insert(0, str(HERE))
    from gen_data import make_csv
    work = Path(tempfile.mkdtemp(prefix="engines-"))
    n = 3_000_000
    source = make_csv(work / "events.csv", n, dirty=0.02)
    child = work / "child.py"
    child.write_text(CHILD, encoding="utf-8")
    print(f"{n:,} linhas, {os.path.getsize(source) / 1e6:.0f} MB; tarefa: receita por país (com a limpeza e o filtro das linhas ruins)\n")
    print(f"  {'motor':<30} {'tempo':>8} {'pico de memória':>16}  resultado igual?")
    results = {}
    for label, engine in [("Python puro (csv + dict)", "python_dict"), ("pandas (read_csv padrão)", "pandas_default"),
                          ("pandas (engine pyarrow)", "pandas_arrow"), ("Polars (eager)", "polars_eager"),
                          ("Polars (lazy + streaming)", "polars_lazy"), ("SQLite (importar + SQL)", "sqlite_sql")]:
        proc = subprocess.run([sys.executable, str(child), engine, str(source)], capture_output=True, text=True, encoding="utf-8")
        if proc.returncode:
            print(f"  {label:<30} ERRO: {proc.stderr.strip()[-200:]}")
            continue
        data = json.loads(proc.stdout.strip().splitlines()[-1])
        results[engine] = data["result"]
        base = results.get("python_dict")
        same = "-" if base is None else all(abs(data["result"].get(k, 0) - v) < 1 for k, v in base.items())
        print(f"  {label:<30} {data['seconds']:7.2f}s {data['peak_mb']:12,.0f} MB   {same}")
    print("\nreceita por país:", results.get("python_dict"))


if __name__ == "__main__":
    main()
