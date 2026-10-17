"""DataFrame e Series: estrutura, tipos, seleção e expressões."""
import numpy as np
import pandas as pd

from sample_data import make_customers, make_orders

print("pandas", pd.__version__, "| numpy", np.__version__)

# 1. Series: um array NumPy + um índice com rótulos
s = pd.Series([10, 20, 30], index=["a", "b", "c"], name="valor")
print("\nSeries:\n", s)
print("s['b'] =", s["b"], "| s.iloc[1] =", s.iloc[1], "| s.to_numpy():", s.to_numpy(), "| dtype:", s.dtype)
print("alinhamento por RÓTULO, não por posição:\n", s + pd.Series({"c": 1, "a": 2, "z": 9}))

# 2. DataFrame: colunas (cada uma com SEU tipo) que compartilham o índice
orders = make_orders(100_000)
customers = make_customers(1_000)
print("\n", orders.head(3).to_string())
print("\nshape:", orders.shape, "| colunas:", list(orders.columns))
print(orders.dtypes.to_string())
print("\nproduct é", orders["product"].dtype, "(texto no pandas 3 = tipo 'str', e o ausente é NaN)")
orders.info(memory_usage="deep")

# 3. dados faltantes e o tipo que aceita ausência
print("\nint com ausente vira float:", pd.Series([1, None, 3]).dtype)
print("Int64 (nullable) mantém int :", pd.Series([1, None, 3], dtype="Int64").tolist(), "| .sum() =", pd.Series([1, None, 3], dtype="Int64").sum())
print("isna():", pd.Series(["a", None]).isna().tolist(), "| NaN != NaN, mas Series.equals trata iguais:", pd.Series([np.nan]).equals(pd.Series([np.nan])))

# 4. selecionar: [] colunas, .loc rótulos, .iloc posições
print("\nloc por rótulo (fim INCLUÍDO):", orders.loc[0:2, "product"].tolist(), "| iloc por posição (fim EXCLUÍDO):", orders.iloc[0:2, 3].tolist())
subset = orders[["order_id", "total"]]
print("colunas:", list(subset.columns), "| uma coluna é Series:", type(orders["total"]).__name__, "| lista de colunas é DataFrame:", type(orders[["total"]]).__name__)

# 5. filtros: máscara booleana (com & | ~ e PARÊNTESES, como no NumPy) ou query()
paid_big = orders[(orders["status"] == "paid") & (orders["total"] > 500)]
same = orders.query("status == 'paid' and total > 500")
print("\nmáscara =", len(paid_big), "linhas | query =", len(same), "| iguais?", paid_big.equals(same))
print("isin:", len(orders[orders["product"].isin(["mouse", "teclado"])]), "| between:", orders["total"].between(100, 200).sum())

# 6. colunas novas SEM alterar o original: assign + pd.col (novo no pandas 3)
enriched = orders.assign(
    net=pd.col("total") * 0.9,
    big=pd.col("total") > 500,
    month=lambda d: d["date"].dt.to_period("M"),
)
print("\nassign com pd.col e lambda:", enriched[["total", "net", "big", "month"]].head(2).to_string())
print("o original não ganhou colunas:", "net" in orders.columns)

# 7. ordenar, ranquear, contar
print("\ntop 3 pedidos:\n", orders.nlargest(3, "total")[["order_id", "product", "total"]].to_string())
print("value_counts:", orders["status"].value_counts().to_dict())
print("normalize :", orders["status"].value_counts(normalize=True).round(3).to_dict())
print("nunique   :", orders["customer_id"].nunique(), "clientes | duplicated:", int(orders.duplicated("order_id").sum()))
print("\ndescribe:\n", orders[["qty", "total"]].describe().round(2).to_string())

# 8. do pandas para o NumPy e de volta: a mesma memória por baixo (Capítulo 11)
arr = orders["total"].to_numpy()
print("\nto_numpy:", arr.dtype, arr.shape, "| soma pelo NumPy:", round(float(arr.sum()), 2), "| pelo pandas:", round(float(orders["total"].sum()), 2))
print("customers:", customers.shape, "| datas de cadastro:", customers["signup"].min().date(), "a", customers["signup"].max().date())
