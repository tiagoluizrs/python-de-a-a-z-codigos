"""O custo das formas de percorrer e transformar um DataFrame."""
import time

import numpy as np
import pandas as pd

from sample_data import make_orders


def best(fn, repeat=3):
    out = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        out.append((time.perf_counter() - start) * 1e3)
    return min(out)


def row(label, ms, base=None):
    extra = f"  ({base / ms:8.1f}x mais rápido)" if base else ""
    print(f"  {label:<50} {ms:10.2f} ms{extra}")


N = 100_000
orders = make_orders(N)

# 1. calcular "total com desconto" linha a linha: de pior a melhor
print(f"1. total com desconto de 10% quando o total passa de 500 ({N:,} linhas)")


def with_iterrows():
    out = []
    for _, r in orders.iterrows():
        out.append(r["total"] * 0.9 if r["total"] > 500 else r["total"])
    return out


def with_itertuples():
    return [t.total * 0.9 if t.total > 500 else t.total for t in orders.itertuples()]


def with_apply():
    return orders.apply(lambda r: r["total"] * 0.9 if r["total"] > 500 else r["total"], axis=1)


def with_series_apply():
    return orders["total"].apply(lambda v: v * 0.9 if v > 500 else v)


def with_where():
    return orders["total"].where(orders["total"] <= 500, orders["total"] * 0.9)


def with_numpy():
    t = orders["total"].to_numpy()
    return np.where(t > 500, t * 0.9, t)


t_rows = best(with_iterrows, 1)
row("iterrows (um objeto Series por linha)", t_rows)
row("apply(axis=1) com lambda", best(with_apply, 1), t_rows)
row("itertuples (namedtuples)", best(with_itertuples), t_rows)
row("Series.apply(lambda v: ...)", best(with_series_apply), t_rows)
row("Series.where (vetorizado)", best(with_where), t_rows)
row("np.where sobre to_numpy()", best(with_numpy), t_rows)
print("  mesmo resultado?", np.allclose(with_numpy(), pd.Series(with_where()).to_numpy()), "(iterrows e apply: o mesmo)")

# 2. crescer um DataFrame em um laço: custo QUADRÁTICO
print("\n2. montar um DataFrame de 2.000 linhas")
records = [{"id": i, "value": i * 2.0} for i in range(2_000)]


def concat_in_loop():
    frame = pd.DataFrame(columns=["id", "value"])
    for rec in records:
        frame = pd.concat([frame, pd.DataFrame([rec])], ignore_index=True)
    return frame


t_loop = best(concat_in_loop, 1)
row("pd.concat dentro de um laço", t_loop)
row("pd.DataFrame(lista de dicts) uma vez", best(lambda: pd.DataFrame(records)), t_loop)
row("pd.concat([...]) uma vez", best(lambda: pd.concat([pd.DataFrame([r]) for r in records], ignore_index=True), 1), t_loop)

# 3. texto: o acessor .str é um laço em C?
print("\n3. operações com texto em 100 mil linhas")
names = pd.Series([f"cliente {i:06d} - são paulo" for i in range(N)])
t_py = best(lambda: [s.upper().replace("SÃO ", "") for s in names.tolist()])
row("compreensão de lista em Python", t_py)
row("names.str.upper().str.replace(...)", best(lambda: names.str.upper().str.replace("SÃO ", "", regex=False)), t_py)
row("names.str.contains('sao') regex", best(lambda: names.str.contains("são paulo")), t_py)

# 4. isin e merge contra o laço `in lista`
print("\n4. filtrar por uma lista de 1.000 clientes")
wanted = list(range(1, 1_001))
wanted_set = set(wanted)
t_list = best(lambda: [c in wanted for c in orders["customer_id"].tolist()], 1)
row("[c in lista for c in ...]", t_list)
row("[c in conjunto for c in ...]", best(lambda: [c in wanted_set for c in orders["customer_id"].tolist()]), t_list)
row("orders['customer_id'].isin(wanted)", best(lambda: orders["customer_id"].isin(wanted)), t_list)

# 5. groupby: a agregação roda em C; o apply com lambda, não
print("\n5. total por cliente (100 mil pedidos, 1.000 clientes)")
t_gapply = best(lambda: orders.groupby("customer_id")["total"].apply(lambda s: s.sum()), 1)
row("groupby().apply(lambda s: s.sum())", t_gapply)
row("groupby().agg('sum')", best(lambda: orders.groupby("customer_id")["total"].sum()), t_gapply)
row("np.bincount(ids, weights=total)", best(lambda: np.bincount(orders["customer_id"], weights=orders["total"])), t_gapply)

# 6. ordenar e achar o maior
print("\n6. os 10 maiores totais")
row("sort_values().head(10)", best(lambda: orders.sort_values("total", ascending=False).head(10)))
row("nlargest(10, 'total')", best(lambda: orders.nlargest(10, "total")))

# 7. eval e query: pouco para dados pequenos, muito para expressões longas em dados grandes
big = pd.DataFrame(np.random.default_rng(0).random((3_000_000, 3)), columns=list("abc"))
print("\n7. a*b + c com 3 milhões de linhas")
row("big['a'] * big['b'] + big['c']", best(lambda: big["a"] * big["b"] + big["c"]))
row("big.eval('a * b + c') (sem numexpr instalado)", best(lambda: big.eval("a * b + c")))
