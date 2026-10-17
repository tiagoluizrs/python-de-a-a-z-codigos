"""Visualização: do DataFrame ao gráfico, com Matplotlib (imagem estática) e Plotly (HTML interativo).

Os arquivos saem em ``saida/`` (ignorada pelo git). Rode e abra os PNG/HTML gerados.
"""
import os
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                                 # sem janela: serve em servidor, container e testes
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px

from sample_data import make_customers, make_orders

OUT = Path(__file__).parent / "saida"
OUT.mkdir(exist_ok=True)

orders = make_orders(100_000)
customers = make_customers(1_000)
paid = orders[orders["status"] == "paid"]
print("matplotlib", matplotlib.__version__, "| backend:", matplotlib.get_backend())

# 1. o jeito rápido: df.plot() devolve um Axes do Matplotlib
daily = paid.set_index("date")["total"].resample("D").sum()
ax = daily.rolling(7).mean().plot(figsize=(8, 3.5), title="Receita diária (média móvel de 7 dias)", color="#c2410c", legend=False)
ax.set_ylabel("R$")
ax.figure.tight_layout()
ax.figure.savefig(OUT / "receita_diaria.png", dpi=150)
plt.close(ax.figure)

# 2. o jeito explícito (orientado a objetos): Figure e Axes, o que você usa em código de verdade
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
by_product = paid.groupby("product")["total"].sum().sort_values()
axes[0].barh(by_product.index, by_product.to_numpy() / 1e6, color="#0e6b8a")
axes[0].set_title("Receita por produto")
axes[0].set_xlabel("R$ milhões")
axes[1].hist(paid["total"], bins=40, color="#6d28d9")
axes[1].set_yscale("log")
axes[1].set_title("Distribuição do valor dos pedidos (escala log)")
axes[1].set_xlabel("R$")
fig.tight_layout()
fig.savefig(OUT / "produtos_e_distribuicao.png", dpi=150)
plt.close(fig)

# 3. mapa de calor: dia da semana x hora
heat = (orders.assign(weekday=orders["date"].dt.dayofweek, hour=orders["date"].dt.hour)
        .pivot_table(index="weekday", columns="hour", values="order_id", aggfunc="count"))
fig, ax = plt.subplots(figsize=(9, 3))
image = ax.imshow(heat.to_numpy(), aspect="auto", cmap="YlOrRd")
ax.set_yticks(range(7), ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"])
ax.set_xlabel("hora do dia")
ax.set_title("Pedidos por dia da semana e hora")
fig.colorbar(image, label="pedidos")
fig.tight_layout()
fig.savefig(OUT / "mapa_de_calor.png", dpi=150)
plt.close(fig)

# 4. gráfico que MENTE: o mesmo dado, eixos diferentes
sample = paid.groupby("product")["total"].mean().sort_values()
fig, axes = plt.subplots(1, 2, figsize=(9, 3))
axes[0].bar(sample.index, sample.to_numpy(), color="#475569")
axes[0].set_title("Eixo começa em zero")
axes[1].bar(sample.index, sample.to_numpy(), color="#b91c1c")
axes[1].set_ylim(sample.min() * 0.9, sample.max() * 1.02)
axes[1].set_title("Eixo cortado: exagera diferenças")
for a in axes:
    a.tick_params(axis="x", rotation=45)
fig.tight_layout()
fig.savefig(OUT / "eixo_que_mente.png", dpi=150)
plt.close(fig)

# 5. Plotly: HTML interativo (zoom, passar o mouse), ideal para relatórios e dashboards
fig = px.scatter(customers.merge(paid.groupby("customer_id")["total"].agg(["sum", "count"]).reset_index(), on="customer_id"),
                 x="count", y="sum", color="segment", hover_data=["city", "name"],
                 labels={"count": "pedidos pagos", "sum": "receita (R$)"}, title="Clientes: pedidos x receita")
fig.write_html(OUT / "clientes.html", include_plotlyjs="cdn")
print("\narquivos gerados em", OUT.relative_to(Path(__file__).parent.parent))
for path in sorted(OUT.iterdir()):
    print(f"  {path.name:<32} {os.path.getsize(path) / 1e3:8.1f} kB")

# 6. o custo: Matplotlib desenha cada ponto; para milhões, agregue ANTES de desenhar
points = np.random.default_rng(0).normal(size=(2_000_000, 2))
fig, ax = plt.subplots()
start = time.perf_counter()
ax.scatter(points[:200_000, 0], points[:200_000, 1], s=1)
fig.savefig(OUT / "dispersao_200mil.png", dpi=80)
t_scatter = (time.perf_counter() - start) * 1e3
plt.close(fig)
fig, ax = plt.subplots()
start = time.perf_counter()
ax.hexbin(points[:, 0], points[:, 1], gridsize=60, cmap="magma")
fig.savefig(OUT / "hexbin_2milhoes.png", dpi=80)
t_hex = (time.perf_counter() - start) * 1e3
plt.close(fig)
print(f"\nscatter de 200 mil pontos: {t_scatter:6.0f} ms | hexbin (agrega) de 2 MILHÕES: {t_hex:6.0f} ms")
