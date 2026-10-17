"""Polars: DataFrame, tipos, nulos, expressões e contextos."""
import polars as pl

from sample_data import make_orders

print("polars", pl.__version__, "| threads:", pl.thread_pool_size())
orders = make_orders(100_000)

# 1. DataFrame: colunas tipadas, SEM índice (a posição é só a posição)
print("\n", orders.head(3))
print("shape:", orders.shape, "| schema:", dict(orders.schema))
print("estimated_size:", f"{orders.estimated_size('mb'):.1f} MB", "| texto é String (Arrow), nunca object")

# 2. nulos: um conceito só, para TODOS os tipos; NaN é só um float especial
df = pl.DataFrame({"a": [1, 2, None], "f": [1.0, float("nan"), None]})
print("\nint com nulo continua Int64:", df.schema["a"], "| soma:", df["a"].sum(), "| média ignora nulo:", df["a"].mean())
print("float: NaN e null são coisas diferentes:\n", df.select(nan=pl.col("f").is_nan().sum(), null=pl.col("f").is_null().sum(),
                                                              mean=pl.col("f").mean()))

# 3. expressão: uma DESCRIÇÃO de cálculo (não executa nada sozinha), que os contextos aplicam
expr = (pl.col("total") * 0.9).alias("net")
print("\nexpressão:", expr, "| tipo:", type(expr).__name__)

# 4. contextos: select, with_columns, filter, group_by, sort
out = (
    orders
    .filter((pl.col("status") == "paid") & (pl.col("total") > 500))
    .with_columns(net=pl.col("total") * 0.9, month=pl.col("date").dt.month())
    .select("order_id", "product", "total", "net", "month")
    .sort("total", descending=True)
)
print("\nfilter -> with_columns -> select -> sort:", out.shape, "\n", out.head(3))
print("o original continua com", len(orders.columns), "colunas (nada é alterado no lugar)")

# 5. várias agregações em UM group_by (cada expressão é independente e roda em paralelo)
report = (
    orders.filter(pl.col("status") == "paid")
    .group_by("product")
    .agg(orders=pl.len(), units=pl.col("qty").sum(), revenue=pl.col("total").sum(), avg_ticket=pl.col("total").mean())
    .sort("revenue", descending=True)
)
print("\nreceita por produto:\n", report)

# 6. condicional: when/then/otherwise (o if/else vetorizado)
tiers = orders.select(
    pl.when(pl.col("total") >= 1000).then(pl.lit("alto"))
    .when(pl.col("total") >= 100).then(pl.lit("médio"))
    .otherwise(pl.lit("baixo")).alias("faixa")
)
print("\nfaixas:", tiers["faixa"].value_counts(sort=True).to_dicts())

# 7. janelas: over() faz o 'groupby + transform' do pandas dentro de uma expressão
ranked = orders.select(
    "product", "total",
    share=pl.col("total") / pl.col("total").sum().over("product"),
    rank=pl.col("total").rank("ordinal", descending=True).over("product"),
)
print("\nover('product'): soma das participações por produto =", ranked.group_by("product").agg(pl.col("share").sum().round(6))["share"].unique().to_list())

# 8. seletores: escolher colunas por tipo, nome ou padrão
import polars.selectors as cs
print("\nnuméricas:", orders.select(cs.numeric()).columns, "| texto:", orders.select(cs.string()).columns, "| datas:", orders.select(cs.temporal()).columns)
print("arredondar todas as float de uma vez:", orders.select(cs.float().round(0)).head(2).rows())

# 9. namespaces de texto e data
names = pl.DataFrame({"raw": ["  Ana Souza ", "bruno LIMA", None]})
print("\n", names.with_columns(clean=pl.col("raw").str.strip_chars().str.to_titlecase(), size=pl.col("raw").str.len_chars()))
print("dt:", orders.select(weekday=pl.col("date").dt.weekday(), hour=pl.col("date").dt.hour(), month_start=pl.col("date").dt.truncate("1mo")).head(2).rows())

# 10. tipos aninhados: lista e struct como cidadãos de primeira classe
nested = orders.group_by("customer_id").agg(items=pl.col("product")).head(2)
print("\nlista por grupo:", nested.schema["items"], "| tamanho de cada lista:", nested.select(n=pl.col("items").list.len())["n"].to_list())
packed = orders.select(pl.struct("product", "qty").alias("line")).head(1)
print("struct:", packed.schema["line"], packed["line"].to_list())

# 11. converter para o mundo de fora
print("\nto_numpy:", orders["total"].to_numpy().dtype, "| to_list:", orders["qty"].head(3).to_list(), "| to_dicts:", orders.head(1).to_dicts()[0]["product"])
