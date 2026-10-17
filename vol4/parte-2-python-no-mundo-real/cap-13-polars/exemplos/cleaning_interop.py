"""Limpeza com expressões, tipos categóricos e a ponte com pandas, Arrow e NumPy."""
import numpy as np
import polars as pl

from sample_data import make_dirty_orders, make_orders

raw = make_dirty_orders()
print("como chegou:\n", raw)

# 1. a limpeza inteira é UMA expressão por coluna, dentro de UM with_columns
money = (
    pl.col("amount").str.replace("R$", "", literal=True).str.strip_chars()
    .str.replace_all(".", "", literal=True).str.replace(",", ".", literal=True)
    .cast(pl.Float64, strict=False)                         # strict=False: o que não converte vira null
)
date = pl.coalesce(                                          # tenta um formato, depois o outro
    pl.col("date").str.to_date("%Y-%m-%d", strict=False),
    pl.col("date").str.to_date("%d/%m/%Y", strict=False),
)
clean = (
    raw.rename(lambda c: c.strip().lower().replace(" ", "_"))
    .unique(maintain_order=True)                             # duplicatas exatas, na ordem de chegada
    .with_columns(
        order_id=pl.col("order_id").cast(pl.Int64, strict=False),
        customer=pl.col("customer").str.strip_chars().str.to_titlecase().replace("", None),
        date=date,
        amount=money,
        status=pl.col("status").str.to_lowercase().cast(pl.Enum(["paid", "pending", "cancelled"])),
    )
)
print("\nlimpo:\n", clean)

# 2. relatório do que foi descartado, em vez de sumir com as linhas
valid = pl.all_horizontal(pl.col("order_id", "customer", "date", "amount").is_not_null())
print("válidas:", clean.filter(valid).height, "| rejeitadas:", clean.filter(~valid).height)
print("nulos por coluna:", clean.null_count().row(0, named=True))

# 3. Enum: categorias FIXAS (valida na entrada) x Categorical (aprende as categorias que aparecem)
try:
    pl.Series(["paid", "refunded"]).cast(pl.Enum(["paid", "pending", "cancelled"]))
except Exception as error:
    print("\nEnum recusa valor fora da lista ->", type(error).__name__)
orders = make_orders(500_000)
as_cat = orders.with_columns(pl.col("product").cast(pl.Categorical), pl.col("status").cast(pl.Enum(["paid", "pending", "cancelled"])))
print(f"memória: String {orders.estimated_size('mb'):.1f} MB | com Categorical/Enum {as_cat.estimated_size('mb'):.1f} MB")

# 4. pandas, Arrow e NumPy: a ponte quase sempre é uma cópia barata ou nenhuma
arrow = orders.to_arrow()
numbers = orders["total"].to_numpy()
print("\nto_arrow:", type(arrow).__name__, arrow.schema.field("product").type, "| from_arrow igual?", pl.from_arrow(arrow).equals(orders))
print("to_numpy de uma coluna sem nulos:", numbers.dtype, "| somente leitura?", not numbers.flags.writeable, "(sem copiar)")
pdf = orders.head(1000).to_pandas()
print("to_pandas:", type(pdf).__name__, dict(pdf.dtypes.astype(str).head(3)), "| volta igual?", pl.from_pandas(pdf).equals(orders.head(1000)))
print("from_numpy:", pl.from_numpy(np.arange(6).reshape(3, 2), schema=["a", "b"], orient="row").to_dicts()[:2])

# 5. Series: os métodos que o pandas também tem
s = pl.Series("v", [1, 2, 3, 4, 5, 6])
print("\nSeries:", s.cum_sum().to_list(), "| rolling_mean(3):", s.rolling_mean(3).to_list(), "| diff:", s.diff().to_list())
print("is_in:", s.is_in([2, 4]).to_list(), "| clip:", s.clip(2, 4).to_list(), "| shift(1):", s.shift(1).to_list())

# 6. fill_null com estratégias; null não é NaN
t = pl.Series("t", [1.0, None, None, 4.0, float("nan")])
print("\nforward:", t.fill_null(strategy="forward").to_list(), "| interpolate:", t.interpolate().to_list(), "| fill_nan(0):", t.fill_nan(0).to_list())
