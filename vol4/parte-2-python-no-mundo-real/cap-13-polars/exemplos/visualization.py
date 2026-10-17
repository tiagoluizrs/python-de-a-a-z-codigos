"""Visualização a partir do Polars: Matplotlib, Plotly e as janelas temporais.

Os arquivos saem em ``saida/`` (ignorada pelo git).
"""
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.express as px
import polars as pl

from sample_data import make_customers, make_orders

OUT = Path(__file__).parent / "saida"
OUT.mkdir(exist_ok=True)
orders = make_orders(300_000)
customers = make_customers(1_000)
paid = orders.filter(pl.col("status") == "paid")

# 1. a regra: agregue NO POLARS (rápido, em paralelo) e entregue só o resultado pequeno ao gráfico
weekly = (
    paid.sort("date")
    .group_by_dynamic("date", every="1w")                 # janela de tempo: o resample do pandas
    .agg(revenue=pl.col("total").sum(), orders=pl.len())
)
print("semanas:", weekly.height, "| primeiras:", weekly.head(2).rows())

# 2. Matplotlib aceita listas e arrays: to_numpy() e to_list() bastam (nada de to_pandas)
fig, ax = plt.subplots(figsize=(8, 3.5))
ax.plot(weekly["date"].to_list(), weekly["revenue"].to_numpy() / 1e3, color="#c2410c")
ax.set_title("Receita semanal (R$ mil)")
ax.set_ylabel("R$ mil")
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(OUT / "receita_semanal.png", dpi=150)
plt.close(fig)

# 3. barras: receita por produto
by_product = paid.group_by("product").agg(pl.col("total").sum().alias("revenue")).sort("revenue")
fig, ax = plt.subplots(figsize=(6, 3.2))
ax.barh(by_product["product"].to_list(), by_product["revenue"].to_numpy() / 1e6, color="#0e6b8a")
ax.set_xlabel("R$ milhões")
ax.set_title("Receita por produto")
fig.tight_layout()
fig.savefig(OUT / "receita_por_produto.png", dpi=150)
plt.close(fig)

# 4. Plotly Express aceita DataFrames do Polars DIRETAMENTE (sem to_pandas)
per_customer = (
    paid.group_by("customer_id").agg(revenue=pl.col("total").sum(), orders=pl.len())
    .join(customers, on="customer_id")
)
fig = px.scatter(per_customer, x="orders", y="revenue", color="segment", hover_data=["city", "name"],
                 title="Clientes: pedidos x receita")
fig.write_html(OUT / "clientes.html", include_plotlyjs="cdn")

# 5. o gráfico de um resumo de dois eixos: pivot no Polars, imshow no Matplotlib
heat = (
    orders.with_columns(weekday=pl.col("date").dt.weekday(), hour=pl.col("date").dt.hour())
    .group_by("weekday", "hour").agg(n=pl.len())
    .pivot(on="hour", index="weekday", values="n")
    .sort("weekday")
)
matrix = heat.drop("weekday").select(sorted(heat.columns[1:], key=int)).to_numpy()
fig, ax = plt.subplots(figsize=(9, 3))
image = ax.imshow(matrix, aspect="auto", cmap="YlOrRd")
ax.set_yticks(range(7), ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"])
ax.set_xlabel("hora do dia")
ax.set_title("Pedidos por dia da semana e hora")
fig.colorbar(image, label="pedidos")
fig.tight_layout()
fig.savefig(OUT / "mapa_de_calor.png", dpi=150)
plt.close(fig)

print("\narquivos gerados:")
for path in sorted(OUT.iterdir()):
    print(f"  {path.name:<28} {os.path.getsize(path) / 1e3:8.1f} kB")
print("heat:", matrix.shape, "| soma =", int(matrix.sum()), "(= todos os pedidos:", orders.height, ")")
