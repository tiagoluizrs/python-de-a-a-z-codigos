"""Ler e gravar: CSV, Parquet, Excel, JSON Lines, SQLite e leitura em pedaços."""
import os
import sqlite3
import tempfile
import time
from pathlib import Path

import pandas as pd

from sample_data import make_orders

work = Path(tempfile.mkdtemp(prefix="pandas-cap64-"))
orders = make_orders(300_000)


def timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, (time.perf_counter() - start) * 1e3


def size(path):
    return os.path.getsize(path) / 1e6


print(f"{len(orders):,} pedidos em memória\n")

# 1. CSV x Parquet: texto x colunas binárias comprimidas, com os tipos preservados
_, t_csv_w = timed(lambda: orders.to_csv(work / "orders.csv", index=False))
csv_back, t_csv_r = timed(lambda: pd.read_csv(work / "orders.csv", parse_dates=["date"]))
_, t_pq_w = timed(lambda: orders.to_parquet(work / "orders.parquet"))
pq_back, t_pq_r = timed(lambda: pd.read_parquet(work / "orders.parquet"))
print(f"CSV     : {size(work / 'orders.csv'):6.1f} MB | gravar {t_csv_w:7.0f} ms | ler {t_csv_r:7.0f} ms")
print(f"Parquet : {size(work / 'orders.parquet'):6.1f} MB | gravar {t_pq_w:7.0f} ms | ler {t_pq_r:7.0f} ms")
print("Parquet devolve os MESMOS tipos?", pq_back.dtypes.equals(orders.dtypes), "| CSV (com parse_dates, e só porque os textos eram simples):", csv_back.dtypes.equals(orders.dtypes))

# 2. Parquet lê só as colunas (e só as linhas) que você pede
cols, t_cols = timed(lambda: pd.read_parquet(work / "orders.parquet", columns=["customer_id", "total"]))
filt, t_filt = timed(lambda: pd.read_parquet(work / "orders.parquet", columns=["product", "total"], filters=[("product", "==", "monitor")]))
print(f"\nread_parquet(columns=[2 de 8]) {t_cols:5.0f} ms | com filters=product=='monitor': {len(filt):,} linhas em {t_filt:5.0f} ms")

# 3. leitura em pedaços: arquivo maior que a memória
total, rows = 0.0, 0
start = time.perf_counter()
for chunk in pd.read_csv(work / "orders.csv", usecols=["total", "status"], chunksize=50_000):
    total += chunk.loc[chunk["status"] == "paid", "total"].sum()
    rows += len(chunk)
print(f"\nchunksize=50_000: {rows:,} linhas lidas aos poucos em {(time.perf_counter() - start) * 1e3:.0f} ms | total pago {total:,.2f}"
      f" | confere? {abs(total - orders.loc[orders['status'] == 'paid', 'total'].sum()) < 1e-6}")

# 4. JSON Lines: um objeto por linha, o formato de logs e de APIs em lote
sample = orders.head(1_000)
sample.to_json(work / "orders.jsonl", orient="records", lines=True, date_format="iso")
back = pd.read_json(work / "orders.jsonl", lines=True)
print(f"\nJSON Lines: {size(work / 'orders.jsonl'):.2f} MB para 1.000 linhas | volta com {len(back)} linhas e colunas {back.columns.tolist()[:3]}...")

# 5. Excel: conveniente, lento e limitado (1.048.576 linhas); bom para entregar, ruim para guardar
small = orders.head(20_000)
_, t_xl_w = timed(lambda: small.to_excel(work / "orders.xlsx", index=False, sheet_name="pedidos"))
_, t_xl_r = timed(lambda: pd.read_excel(work / "orders.xlsx", sheet_name="pedidos"))
_, t_pq_s = timed(lambda: small.to_parquet(work / "small.parquet"))
print(f"\nExcel de 20.000 linhas: gravar {t_xl_w:6.0f} ms | ler {t_xl_r:6.0f} ms | {size(work / 'orders.xlsx'):.2f} MB (Parquet: {t_pq_s:.0f} ms)")

# 6. SQLite: to_sql e read_sql (o Capítulo 1 mostrou o banco; o pandas só empacota)
conn = sqlite3.connect(work / "orders.db")
_, t_sql_w = timed(lambda: orders.to_sql("orders", conn, index=False, if_exists="replace", chunksize=50_000))
result, t_sql_r = timed(lambda: pd.read_sql_query("SELECT product, SUM(total) AS revenue FROM orders WHERE status = ? GROUP BY product ORDER BY 2 DESC", conn, params=("paid",)))
print(f"\nto_sql: {t_sql_w:6.0f} ms | agregar NO BANCO e trazer 6 linhas: {t_sql_r:5.0f} ms\n", result.round(0).to_string(index=False))
pulled, t_pull = timed(lambda: pd.read_sql_query("SELECT * FROM orders", conn, parse_dates=["date"]))
print(f"trazer a tabela inteira e agregar no pandas: {t_pull:5.0f} ms só para ler {len(pulled):,} linhas (filtre e agregue no banco)")
conn.close()

# 7. clipboard, HTML e Markdown: úteis para olhar e colar, não para pipelines
print("\nto_markdown precisa do tabulate; to_html:", len(orders.head(3).to_html()), "caracteres | to_string:", len(orders.head(3).to_string()), "caracteres")

# 8. segurança: read_pickle executa código (Capítulo 8 do Volume 3). Troque dados em Parquet, CSV ou JSON.
print("read_pickle de fonte desconhecida = executar código de desconhecido; prefira Parquet")
