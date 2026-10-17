"""Formatos de arquivo, compressão, conjuntos particionados e o banco de dados."""
import os
import sqlite3
import tempfile
import time
from pathlib import Path

import polars as pl

from sample_data import make_orders

work = Path(tempfile.mkdtemp(prefix="polars-io-"))
orders = make_orders(1_000_000)


def timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, (time.perf_counter() - start) * 1e3


def mb(path):
    return sum(f.stat().st_size for f in Path(path).rglob("*") if f.is_file()) / 1e6 if Path(path).is_dir() else os.path.getsize(path) / 1e6


print(f"{orders.height:,} pedidos ({orders.estimated_size('mb'):.0f} MB em memória)\n")

# 1. formatos: tamanho e tempo de gravar e de ler tudo
rows = []
for name, write, read in [
    ("CSV", lambda p: orders.write_csv(p), lambda p: pl.read_csv(p, try_parse_dates=True)),
    ("NDJSON (JSON Lines)", lambda p: orders.write_ndjson(p), lambda p: pl.read_ndjson(p)),
    ("Parquet (zstd, padrão)", lambda p: orders.write_parquet(p), lambda p: pl.read_parquet(p)),
    ("Parquet (sem compressão)", lambda p: orders.write_parquet(p, compression="uncompressed"), lambda p: pl.read_parquet(p)),
    ("Arrow IPC (Feather v2)", lambda p: orders.write_ipc(p), lambda p: pl.read_ipc(p)),
]:
    path = work / f"orders-{len(rows)}"
    _, t_w = timed(lambda: write(path))
    _, t_r = timed(lambda: read(path))
    print(f"  {name:<26} {mb(path):7.1f} MB | gravar {t_w:7.0f} ms | ler {t_r:7.0f} ms")
    rows.append(name)

# 2. conjunto PARTICIONADO: uma pasta por valor de uma coluna; o scan lê só as pastas que a consulta precisa
orders.write_parquet(work / "by-status", partition_by="status")
folders = sorted(p.name for p in (work / "by-status").iterdir())
print("\nparticionado por status:", folders)
paid_plan = pl.scan_parquet(work / "by-status", hive_partitioning=True).filter(pl.col("status") == "paid").select(pl.len())
print("linhas paid (lendo SÓ a pasta status=paid):", paid_plan.collect().item(), "| plano:", [line.strip() for line in paid_plan.explain().splitlines() if "SCAN" in line or "SELECTION" in line][:2])

# 3. vários arquivos como um só: glob no scan
for i, chunk in enumerate(orders.iter_slices(250_000)):
    chunk.write_parquet(work / f"part-{i}.parquet")
total = pl.scan_parquet(work / "part-*.parquet").select(pl.col("total").sum(), pl.len()).collect()
print("\nscan_parquet('part-*.parquet'):", total.row(0), "| igual ao original?", abs(total["total"][0] - orders["total"].sum()) < 1e-3)

# 4. schema explícito na leitura de CSV: sem adivinhação, sem surpresa
csv = work / "orders-0"
schema = {"order_id": pl.Int64, "customer_id": pl.Int32, "date": pl.Datetime("us"), "product": pl.Categorical, "qty": pl.UInt8,
          "unit_price": pl.Float32, "status": pl.Enum(["paid", "pending", "cancelled"]), "total": pl.Float64}
typed, t_typed = timed(lambda: pl.read_csv(csv, schema_overrides=schema, try_parse_dates=True))
plain, t_plain = timed(lambda: pl.read_csv(csv, try_parse_dates=True))
print(f"\nread_csv com schema_overrides: {t_typed:5.0f} ms, {typed.estimated_size('mb'):.0f} MB | sem: {t_plain:5.0f} ms, {plain.estimated_size('mb'):.0f} MB")

# 5. banco de dados: read_database com uma conexão DB-API (sqlite3 aqui; o Capítulo 1)
conn = sqlite3.connect(work / "orders.db")
conn.execute("create table orders (order_id integer, status text, total real)")
conn.executemany("insert into orders values (?, ?, ?)", orders.head(200_000).select("order_id", "status", "total").iter_rows())
conn.commit()
agg, t_db = timed(lambda: pl.read_database("select status, sum(total) as revenue, count(*) as n from orders group by status order by 2 desc", conn))
print(f"\nread_database (agregado no banco): {t_db:.0f} ms ->", agg.to_dicts()[:2])
conn.close()

# 6. sink em streaming: converter um arquivo grande sem carregá-lo
(pl.scan_csv(csv).filter(pl.col("status") == "paid").sink_parquet(work / "paid-only.parquet"))
print("\nsink_parquet a partir de scan_csv:", pl.scan_parquet(work / "paid-only.parquet").select(pl.len()).collect().item(), "linhas pagas,", f"{mb(work / 'paid-only.parquet'):.1f} MB")
