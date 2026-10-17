"""A API preguiçosa: o plano da consulta, a otimização e os motores (em memória x streaming)."""
import os
import tempfile
import time
from pathlib import Path

import polars as pl

from sample_data import make_orders

work = Path(tempfile.mkdtemp(prefix="polars-cap65-"))
orders = make_orders(2_000_000)
orders.write_parquet(work / "orders.parquet")
orders.write_csv(work / "orders.csv")
print(f"2 milhões de pedidos: parquet {os.path.getsize(work / 'orders.parquet') / 1e6:.0f} MB | csv {os.path.getsize(work / 'orders.csv') / 1e6:.0f} MB\n")


def best(fn, repeat=3):
    out = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        out.append((time.perf_counter() - start) * 1e3)
    return min(out)


# 1. LazyFrame: nada executa até o .collect(); o resultado é um PLANO
query = (
    pl.scan_parquet(work / "orders.parquet")
    .filter(pl.col("status") == "paid")
    .group_by("product")
    .agg(revenue=pl.col("total").sum(), orders=pl.len())
    .sort("revenue", descending=True)
)
print("tipo:", type(query).__name__, "| nada foi lido do disco ainda")
print("\nplano otimizado:\n" + query.explain())

# 2. o otimizador empurra o filtro e as colunas para dentro da leitura (predicate e projection pushdown)
print("\nplano sem otimização:\n" + query.explain(optimizations=pl.QueryOptFlags.none()))

# 3. quanto vale: ler tudo e processar no eager x scan preguiçoso que lê só 3 colunas
def eager():
    df = pl.read_parquet(work / "orders.parquet")
    return df.filter(pl.col("status") == "paid").group_by("product").agg(revenue=pl.col("total").sum()).sort("revenue")


def lazy():
    return (pl.scan_parquet(work / "orders.parquet").filter(pl.col("status") == "paid")
            .group_by("product").agg(revenue=pl.col("total").sum()).sort("revenue").collect())


t_eager, t_lazy = best(eager), best(lazy)
print(f"\nlido e agregado: eager (read_parquet) {t_eager:6.0f} ms | lazy (scan_parquet) {t_lazy:6.0f} ms ({t_eager / t_lazy:.1f}x)")
a_res, b_res = eager(), lazy()
diff = (a_res["revenue"] - b_res["revenue"]).abs().max()
print("mesmo resultado?", a_res["product"].to_list() == b_res["product"].to_list(), f"| maior diferença de receita: {diff:.1e} (soma em paralelo arredonda diferente)")

# 4. CSV: o scan preguiçoso só parseia o que a consulta precisa
t_csv_eager = best(lambda: pl.read_csv(work / "orders.csv").select(pl.col("total").sum()), 2)
t_csv_lazy = best(lambda: pl.scan_csv(work / "orders.csv").select(pl.col("total").sum()).collect(), 2)
print(f"CSV, soma de uma coluna: read_csv {t_csv_eager:6.0f} ms | scan_csv {t_csv_lazy:6.0f} ms ({t_csv_eager / t_csv_lazy:.1f}x)")

# 5. os dois motores: em memória e streaming (processa em blocos, memória limitada)
for engine in ("in-memory", "streaming"):
    ms = best(lambda: query.collect(engine=engine), 3)
    print(f"collect(engine={engine!r:<12}) {ms:7.0f} ms")
print("engine padrão (auto):", f"{best(lambda: query.collect()):.0f} ms")

# 6. sink: processar um arquivo MAIOR que a memória e gravar o resultado sem materializar nada
out = work / "paid.parquet"
start = time.perf_counter()
(pl.scan_parquet(work / "orders.parquet").filter(pl.col("status") == "paid")
 .select("order_id", "customer_id", "total").sink_parquet(out))
print(f"\nsink_parquet (streaming): {(time.perf_counter() - start) * 1e3:.0f} ms | {os.path.getsize(out) / 1e6:.0f} MB | linhas: {pl.scan_parquet(out).select(pl.len()).collect().item():,}")

# 7. APIs removidas no 2.0 avisam com o motivo (LazyFrame.profile só fazia sentido no motor em memória)
try:
    query.profile()
except pl.exceptions.AttributeRemovedError as error:
    print("\nquery.profile() ->", type(error).__name__, "|", str(error)[:95], "...")

# 8. schema sem executar: o plano sabe os tipos de saída
print("\nschema do resultado (sem ler nada):", dict(query.collect_schema()))

# 9. cache de um resultado caro usado duas vezes: .collect() uma vez e reuse, não escreva a consulta duas vezes
base = pl.scan_parquet(work / "orders.parquet").filter(pl.col("status") == "paid").collect()
print("reusando um collect:", base.height, "linhas paid em memória")
