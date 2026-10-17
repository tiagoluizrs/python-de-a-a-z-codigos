"""Gabarito do exercício 6."""
import polars as pl


def top_n(df, by, value, n):
    return (
        df.with_row_index("__pos")
        .sort([by, value, "__pos"], descending=[False, True, False])
        .group_by(by, maintain_order=True).head(n)
        .drop("__pos")
    )


def growth_by_group(df, group, order, value):
    previous = pl.col(value).shift(1).over(group, order_by=order)
    growth = pl.when(previous.is_null() | (previous == 0)).then(None).otherwise((pl.col(value) - previous) / previous * 100)
    return df.sort(group, order).with_columns(growth=growth)


def to_pandas_safely(df):
    nested = [name for name, dtype in df.schema.items() if dtype.is_nested()]
    if nested:
        raise TypeError(f"colunas aninhadas: {nested}")
    pdf = df.to_pandas()
    return pdf, {c: str(t) for c, t in pdf.dtypes.items()}
