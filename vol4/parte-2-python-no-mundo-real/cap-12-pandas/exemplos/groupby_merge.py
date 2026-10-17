"""Agrupar, juntar e remodelar: groupby, merge, pivot, melt, concat."""
import pandas as pd

from sample_data import make_customers, make_orders

orders = make_orders(50_000, n_customers=500)
customers = make_customers(500)
paid = orders[orders["status"] == "paid"]

# 1. groupby: dividir, aplicar, combinar. Agregações com nome (a forma legível e rápida)
by_product = (
    paid.groupby("product")
    .agg(orders=("order_id", "count"), units=("qty", "sum"), revenue=("total", "sum"), avg_ticket=("total", "mean"))
    .sort_values("revenue", ascending=False)
)
print("receita por produto:\n", by_product.round(2).to_string())

# 2. vários níveis e a diferença entre as chaves virarem índice ou coluna
by_city_month = (
    paid.merge(customers[["customer_id", "city"]], on="customer_id")
    .assign(month=lambda d: d["date"].dt.to_period("M").astype(str))
    .groupby(["city", "month"], as_index=False)["total"].sum()
)
print("\ncidade x mês (as_index=False devolve colunas):", by_city_month.shape, "|", by_city_month.columns.tolist())

# 3. transform: devolve algo do TAMANHO da entrada (para comparar cada linha com o seu grupo)
orders_ranked = paid.assign(
    share_of_product=lambda d: d["total"] / d.groupby("product")["total"].transform("sum"),
    rank_in_product=lambda d: d.groupby("product")["total"].rank(method="first", ascending=False),
)
print("\ntransform (participação no total do produto, soma por produto = 1):",
      orders_ranked.groupby("product")["share_of_product"].sum().round(6).unique().tolist())
print("maior pedido de cada produto (rank 1):\n", orders_ranked[orders_ranked["rank_in_product"] == 1][["product", "total"]].drop_duplicates("product").to_string(index=False))

# 4. merge: left, inner, validate e o produto cartesiano silencioso
joined = orders.merge(customers, on="customer_id", how="left", validate="many_to_one")
print("\nmerge left many_to_one:", joined.shape, "| linhas iguais às de orders?", len(joined) == len(orders))
duplicated_customers = pd.concat([customers, customers.head(10)])        # 10 clientes repetidos por engano
blown = orders.merge(duplicated_customers, on="customer_id")
print(f"cadastro com 10 duplicados: o merge sem validate virou {len(blown):,} linhas (eram {len(orders):,})")
try:
    orders.merge(duplicated_customers, on="customer_id", validate="many_to_one")
except pd.errors.MergeError as error:
    print("com validate='many_to_one' ->", type(error).__name__, str(error)[:60], "...")

# 5. anti-join: quem NÃO tem pedido (indicator=True)
some = orders[orders["customer_id"] <= 450]
check = customers.merge(some[["customer_id"]].drop_duplicates(), on="customer_id", how="left", indicator=True)
print("\nclientes sem nenhum pedido (anti-join):", int((check["_merge"] == "left_only").sum()), "| indicator:", check["_merge"].unique().tolist())

# 6. a chave é diferente nos dois lados e os rótulos coincidem nas outras colunas
left = pd.DataFrame({"id": [1, 2], "name": ["a", "b"]})
right = pd.DataFrame({"user": [1, 2], "name": ["x", "y"]})
print("\ncolunas com o mesmo nome ganham sufixos:", left.merge(right, left_on="id", right_on="user", suffixes=("_left", "_right")).columns.tolist())

# 7. pivot_table: o resumo de duas dimensões
pivot = orders.pivot_table(index="product", columns="status", values="total", aggfunc="sum", margins=True, margins_name="TOTAL")
print("\npivot_table (produto x status, com totais):\n", pivot.round(0).to_string())
cross = pd.crosstab(orders["product"], orders["status"], normalize="index").round(3)
print("\ncrosstab normalizado por linha:\n", cross.to_string())

# 8. largo <-> longo: melt e pivot
wide = by_product[["orders", "units"]].reset_index()
long = wide.melt(id_vars="product", var_name="metric", value_name="value")
print("\nmelt (largo -> longo):", wide.shape, "->", long.shape, "|", long.head(3).values.tolist())
back = long.pivot(index="product", columns="metric", values="value").reset_index()
print("pivot volta ao largo?", back[["product", "orders", "units"]].equals(wide[["product", "orders", "units"]].sort_values("product").reset_index(drop=True)))

# 9. concat: empilhar tabelas com as mesmas colunas
parts = [orders.iloc[:1000], orders.iloc[1000:2000]]
print("\nconcat vertical:", pd.concat(parts, ignore_index=True).shape, "| com keys, o primeiro nível do índice:", pd.concat(parts, keys=["jan", "fev"]).index.get_level_values(0).unique().tolist())

# 10. groupby com categoria: observed=True (padrão no pandas 3) não cria grupos vazios
cat = pd.DataFrame({"k": pd.Categorical(["a", "b"], categories=["a", "b", "c"]), "v": [1, 2]})
print("\ngroupby em categoria (pandas 3): ", cat.groupby("k")["v"].sum().to_dict(), "| com observed=False:", cat.groupby("k", observed=False)["v"].sum().to_dict())
