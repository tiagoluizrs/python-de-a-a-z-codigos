"""Expressões em profundidade: janelas, joins, séries temporais, remodelagem e sessões."""
from datetime import datetime

import polars as pl

from sample_data import make_customers, make_orders

orders = make_orders(100_000, n_customers=500)
customers = make_customers(500)

# 1. over(): agregação por grupo SEM perder as linhas (o transform do pandas)
enriched = orders.select(
    "customer_id", "date", "total",
    customer_total=pl.col("total").sum().over("customer_id"),
    pct_of_customer=(pl.col("total") / pl.col("total").sum().over("customer_id") * 100).round(2),
    order_number=pl.col("date").rank("ordinal").over("customer_id"),
    running_total=pl.col("total").cum_sum().over("customer_id", order_by="date"),
)
print("over(): ", enriched.sort("customer_id", "date").head(3).rows())

# 2. filtrar pelo grupo: pedidos dos clientes com 210 pedidos ou mais (sem join, sem apply)
busy = orders.filter(pl.len().over("customer_id") >= 210)
print("\npedidos dos clientes frequentes:", busy.height, "de", orders.height, "| clientes:", busy["customer_id"].n_unique(), "de 500")

# 3. o maior pedido de cada cliente: top_k por grupo
top2 = orders.sort("total", descending=True).group_by("customer_id").head(2)
print("2 maiores pedidos por cliente:", top2.height, "linhas | por produto, o primeiro de cada:", orders.group_by("product").first().height)

# 4. janelas de tempo: group_by_dynamic (resample) e rolling com período
daily = orders.sort("date").group_by_dynamic("date", every="1d").agg(revenue=pl.col("total").sum())
print("\ndiário:", daily.height, "dias | semanal:", orders.sort("date").group_by_dynamic("date", every="1w").agg(pl.col("total").sum()).height, "semanas")
rolled = daily.with_columns(ma7=pl.col("revenue").rolling_mean(7), change=pl.col("revenue").diff(), growth=pl.col("revenue").pct_change())
print("média móvel 7d (início é null):", rolled["ma7"].head(8).round(0).to_list())
by_time = orders.sort("date").rolling("date", period="7d").agg(pl.col("total").sum().alias("sum7d"))
print("rolling por tempo (7d), último:", round(by_time["sum7d"][-1]))

# 5. dias sem pedido: upsample preenche o calendário
weekdays = daily.filter(pl.col("date").dt.weekday() < 6)                      # sem sábado e domingo: buracos no calendário
full = weekdays.upsample("date", every="1d").with_columns(pl.col("revenue").fill_null(0))
print(f"sem fins de semana: {weekdays.height} dias | upsample('1d'): {full.height} dias, {full.filter(pl.col('revenue') == 0).height} preenchidos com 0")

# 6. joins: how, validate, anti e semi (o filtro por existência)
print("\nclientes SEM pedido (anti):", customers.join(orders.filter(pl.col("customer_id") <= 450), on="customer_id", how="anti").height,
      "| COM pedido (semi):", customers.join(orders.filter(pl.col("customer_id") <= 450), on="customer_id", how="semi").height)
duplicated = pl.concat([customers, customers.head(10)])
try:
    orders.join(duplicated, on="customer_id", how="left", validate="m:1")
except pl.exceptions.ComputeError as error:
    print("join com validate='m:1' e chave repetida ->", type(error).__name__, str(error)[:55], "...")
print("sem validate:", orders.join(duplicated, on="customer_id", how="left").height, "linhas (eram", orders.height, ")")
print("join_asof (o valor MAIS RECENTE até a data), exemplo de 3 linhas:")
prices = pl.DataFrame({"since": [datetime(2025, 1, 1), datetime(2025, 6, 1)], "rate": [1.0, 1.1]}).sort("since")
sample = orders.head(3).select("order_id", "date").sort("date")
print(sample.join_asof(prices, left_on="date", right_on="since").select("order_id", "date", "rate").rows())

# 7. remodelar: pivot e unpivot (o largo e o longo)
wide = orders.filter(pl.col("status") == "paid").pivot(on="status", index="product", values="total", aggregate_function="sum")
long = wide.unpivot(index="product", variable_name="status", value_name="revenue")
print("\npivot:", wide.shape, "| unpivot:", long.shape, "| colunas:", long.columns)

# 8. sessões: uma sequência de eventos vira 'visitas' quando o intervalo passa de 30 minutos
events = pl.DataFrame({
    "user": ["a", "a", "a", "a", "b", "b"],
    "ts": [datetime(2026, 1, 1, 10, 0), datetime(2026, 1, 1, 10, 10), datetime(2026, 1, 1, 11, 30), datetime(2026, 1, 1, 11, 40),
           datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 9, 5)],
})
sessions = (
    events.sort("user", "ts")
    .with_columns(new=(pl.col("ts").diff().over("user") > pl.duration(minutes=30)).fill_null(True))
    .with_columns(session=pl.col("new").cum_sum().over("user"))
)
print("\nsessões por usuário:", sessions.group_by("user", "session", maintain_order=True).agg(n=pl.len())["n"].to_list(), "(a: 2+2, b: 2)")

# 9. expressões podem ser guardadas e reutilizadas como funções (composição)
def net(col: str, discount: float = 0.1) -> pl.Expr:
    return (pl.col(col) * (1 - discount)).alias(f"{col}_net")


print("\nexpressão reutilizável:", orders.select(net("total"), net("unit_price", 0.2)).head(2).rows())

# 10. SQL sobre DataFrames, para quem pensa em SQL
ctx = pl.SQLContext(orders=orders)
sql = ctx.execute("select product, count(*) as n, round(sum(total)) as revenue from orders where status = 'paid' group by product order by revenue desc limit 3", eager=True)
print("\nSQLContext:", sql.rows())
