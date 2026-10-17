"""A ordem das linhas NÃO é garantida: group_by, join e o motor streaming (a pegadinha nº 1 do Polars 2)."""
import time

import numpy as np
import polars as pl

rng = np.random.default_rng(0)
df = pl.DataFrame({"user": rng.integers(0, 40, 200_000), "v": rng.random(200_000)})
small = pl.DataFrame({"user": [3, 1, 2], "name": ["c", "a", "b"]})

# 1. group_by: a ordem dos grupos muda de execução para execução
runs = [df.group_by("user").agg(pl.col("v").sum())["user"].to_list()[:6] for _ in range(4)]
print("primeiros grupos em 4 execuções iguais:")
for run in runs:
    print("  ", run)
print("todas iguais?", all(r == runs[0] for r in runs))

# 2. três jeitos de ter ordem: maintain_order, sort, ou nunca depender dela
kept = df.group_by("user", maintain_order=True).agg(pl.col("v").sum())["user"].to_list()[:6]
first_seen = df["user"].unique(maintain_order=True).to_list()[:6]
by_sort = df.group_by("user").agg(pl.col("v").sum()).sort("user")["user"].to_list()[:6]
print("\nmaintain_order=True (ordem da PRIMEIRA aparição):", kept, "| igual ao unique(maintain_order=True):", kept == first_seen)
print("sort('user')                                     :", by_sort, "(determinístico e mais barato de explicar)")

# 3. o custo de manter a ordem
many = pl.DataFrame({"k": rng.integers(0, 1_000_000, 5_000_000), "v": rng.random(5_000_000)})


def best(fn, repeat=3):
    out = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        out.append((time.perf_counter() - start) * 1e3)
    return min(out)


t_free = best(lambda: many.group_by("k").agg(pl.col("v").sum()))
t_kept = best(lambda: many.group_by("k", maintain_order=True).agg(pl.col("v").sum()))
t_sorted = best(lambda: many.group_by("k").agg(pl.col("v").sum()).sort("k"))
print(f"\n5 milhões de linhas, 1 milhão de grupos: sem ordem {t_free:6.0f} ms | maintain_order {t_kept:6.0f} ms | sort no fim {t_sorted:6.0f} ms")

# 4. join: a ordem do resultado também não é garantida
left = pl.DataFrame({"user": list(range(1000)), "x": list(range(1000))})
right = pl.DataFrame({"user": list(range(1000)), "y": list(range(1000, 2000))})
joined = left.lazy().join(right.lazy(), on="user", how="left").collect()
print("\njoin na ordem da esquerda?", joined["user"].to_list() == left["user"].to_list(), "(sem maintain_order, não se promete)")
ordered = left.lazy().join(right.lazy(), on="user", how="left", maintain_order="left").collect()
print("join(..., maintain_order='left')  na ordem da esquerda?", ordered["user"].to_list() == left["user"].to_list())

# 5. a correção que SEMPRE funciona: uma coluna que carrega a ordem
indexed = df.with_row_index("pos").lazy().group_by("user").agg(pl.col("v").sum(), first_pos=pl.col("pos").min()).sort("first_pos").collect()
print("\nwith_row_index + sort: grupos pela primeira aparição:", indexed["user"].to_list()[:6])

# 6. por que isso importa: atribuir resultado por POSIÇÃO a outra tabela
ids = pl.DataFrame({"user": [10, 20, 30]})
totals = pl.DataFrame({"user": [30, 10, 20], "total": [3.0, 1.0, 2.0]})
wrong = ids.with_columns(total=totals["total"])                       # cola por posição: 10 recebe o total do 30
right_way = ids.join(totals, on="user", how="left")
print("\ncolar por posição:", wrong["total"].to_list(), "| join por chave:", right_way["total"].to_list())

# 7. sort é estável quando você pede; sort sem desempate em chave repetida não define a ordem entre iguais
ties = pl.DataFrame({"k": [1, 1, 1, 0], "tag": ["a", "b", "c", "z"]})
print("sort(maintain_order=True):", ties.sort("k", maintain_order=True)["tag"].to_list())
