"""As mesmas operações em Polars e em pandas, e o custo de sair das expressões (UDF em Python)."""
import io
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl

from sample_data import make_customers, make_orders

N = 2_000_000
orders = make_orders(N, n_customers=20_000)
customers = make_customers(20_000)
orders_pd = orders.to_pandas()
customers_pd = customers.to_pandas()
work = Path(tempfile.mkdtemp(prefix="polars-vs-pandas-"))
orders.write_csv(work / "orders.csv")
orders.write_parquet(work / "orders.parquet")


def best(fn, repeat=3):
    out = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        out.append((time.perf_counter() - start) * 1e3)
    return min(out)


def versus(label, pandas_fn, polars_fn, repeat=3):
    t_pd, t_pl = best(pandas_fn, repeat), best(polars_fn, repeat)
    print(f"  {label:<44} pandas {t_pd:8.1f} ms | polars {t_pl:8.1f} ms | {t_pd / t_pl:6.1f}x")


print(f"{N:,} pedidos, {len(customers):,} clientes, {pl.thread_pool_size()} threads\n")
print("tempo (melhor de 3) para a MESMA tarefa:")
versus("ler CSV (130 MB)", lambda: pd.read_csv(work / "orders.csv", parse_dates=["date"]), lambda: pl.read_csv(work / "orders.csv", try_parse_dates=True), 2)
versus("ler Parquet", lambda: pd.read_parquet(work / "orders.parquet"), lambda: pl.read_parquet(work / "orders.parquet"))
versus("filtrar paid e total > 500", lambda: orders_pd[(orders_pd["status"] == "paid") & (orders_pd["total"] > 500)],
       lambda: orders.filter((pl.col("status") == "paid") & (pl.col("total") > 500)))
versus("soma por produto (6 grupos)", lambda: orders_pd.groupby("product")["total"].sum(),
       lambda: orders.group_by("product").agg(pl.col("total").sum()))
versus("soma por cliente (20.000 grupos)", lambda: orders_pd.groupby("customer_id")["total"].sum(),
       lambda: orders.group_by("customer_id").agg(pl.col("total").sum()))
versus("4 agregações por cliente e produto", lambda: orders_pd.groupby(["customer_id", "product"]).agg(n=("order_id", "count"), s=("total", "sum"), m=("total", "mean"), mx=("qty", "max")),
       lambda: orders.group_by("customer_id", "product").agg(n=pl.len(), s=pl.col("total").sum(), m=pl.col("total").mean(), mx=pl.col("qty").max()))
versus("join com 20.000 clientes", lambda: orders_pd.merge(customers_pd, on="customer_id", how="left"),
       lambda: orders.join(customers, on="customer_id", how="left"))
versus("ordenar por total e data", lambda: orders_pd.sort_values(["total", "date"]), lambda: orders.sort("total", "date"))
versus("texto: upper + contém 'on'", lambda: orders_pd["product"].str.upper().str.contains("ON"),
       lambda: orders.select(pl.col("product").str.to_uppercase().str.contains("ON")))
versus("dia da semana e hora da data", lambda: (orders_pd["date"].dt.dayofweek, orders_pd["date"].dt.hour),
       lambda: orders.select(wd=pl.col("date").dt.weekday(), hr=pl.col("date").dt.hour()))
versus("janela: soma móvel de 7 itens por cliente", lambda: orders_pd.sort_values("date").groupby("customer_id")["total"].rolling(7).sum(),
       lambda: orders.sort("date").select(pl.col("total").rolling_sum(7).over("customer_id")), 2)

# 2. memória
mem_pd = orders_pd.memory_usage(deep=True).sum() / 1e6
mem_pl = orders.estimated_size("mb")
print(f"\nmemória do DataFrame: pandas {mem_pd:.0f} MB | polars {mem_pl:.0f} MB")

# 3. o custo de sair do mundo das expressões: UDF em Python
print("\nUDF em Python (map_elements) x expressões nativas, 2 milhões de linhas:")
udf = lambda v: v * 0.9 if v > 500 else v
t_udf = best(lambda: orders.select(pl.col("total").map_elements(udf, return_dtype=pl.Float64)), 1)
t_expr = best(lambda: orders.select(pl.when(pl.col("total") > 500).then(pl.col("total") * 0.9).otherwise(pl.col("total"))))
t_rows = best(lambda: [udf(v) for v in orders["total"]], 1)
t_iter = best(lambda: [r[0] for r in orders.select("total").iter_rows()], 1)
print(f"  map_elements(lambda)            {t_udf:9.0f} ms")
print(f"  when/then/otherwise (expressão) {t_expr:9.1f} ms ({t_udf / t_expr:,.0f}x mais rápido)")
print(f"  [udf(v) for v in coluna]        {t_rows:9.0f} ms (laço Python sobre a Series)")
print(f"  iter_rows() só para ler         {t_iter:9.0f} ms (cria uma tupla por linha)")

# 4. threads: o Polars usa TODOS os núcleos; POLARS_MAX_THREADS limita (vale na partida do processo)
code = (
    "import time, polars as pl, sys; sys.path.insert(0, 'exemplos'); from sample_data import make_orders;"
    "df = make_orders(2_000_000, 20_000);"
    "best = min((lambda: (lambda s: (df.group_by('customer_id', 'product').agg(n=pl.len(), s=pl.col('total').sum()), time.perf_counter() - s)[1])(time.perf_counter()))() for _ in range(3));"
    "print(pl.thread_pool_size(), round(best * 1e3, 1))"
)
print("\ngroup_by de 2 milhões de linhas em um processo novo, variando POLARS_MAX_THREADS:")
base_ms = None
for threads in (1, 2, 4, 8, 16):
    env = {**os.environ, "POLARS_MAX_THREADS": str(threads)}
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env, cwd=Path(__file__).parent.parent).stdout.split()
    ms = float(out[1])
    base_ms = base_ms or ms
    print(f"  {out[0]:>2} threads: {ms:7.1f} ms ({base_ms / ms:4.1f}x)")
