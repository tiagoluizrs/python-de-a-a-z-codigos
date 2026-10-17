"""Tipos e memória: onde o pandas gasta RAM e como reduzir sem perder nada."""
import io
import time

import numpy as np
import pandas as pd

from sample_data import make_orders

orders = make_orders(500_000)


def mb(obj):
    return np.sum(obj.memory_usage(deep=True)) / 1e6        # Series devolve um int; DataFrame, uma Series


print(f"DataFrame de {len(orders):,} pedidos: {mb(orders):.1f} MB\n")
print("memória por coluna (MB):")
print((orders.memory_usage(deep=True) / 1e6).round(2).to_string())

# 1. texto: str (pandas 3, em Arrow) x object (antes) x category
texts = orders["product"]
as_object = texts.astype(object)
as_category = texts.astype("category")
print(f"\ntexto repetido (500 mil pedidos, 6 produtos): str {mb(texts):.1f} MB | object {mb(as_object):.1f} MB | category {mb(as_category):.2f} MB")
print("category guarda 6 textos e 500 mil códigos pequenos:", as_category.cat.categories.tolist(), as_category.cat.codes.dtype)

# 2. inteiros e floats: o menor tipo que cabe (e o cuidado de que "cabe" é decisão sua)
for column in ("qty", "customer_id", "order_id"):
    small = pd.to_numeric(orders[column], downcast="unsigned")
    print(f"{column:<12} int64 {mb(orders[column]):5.1f} MB -> {small.dtype} {mb(small):5.1f} MB")
print("float64 -> float32 perde precisão (dinheiro em centavos como int é mais seguro):",
      np.float32(1234567.89), "(o que sobra de 1234567.89)")

# 3. a "dieta": converter tudo de uma vez e conferir que o conteúdo é o mesmo
slim = orders.astype({"product": "category", "status": "category", "qty": "uint8", "customer_id": "uint16",
                      "unit_price": "float32", "total": "float32", "order_id": "uint32"})
print(f"\nantes {mb(orders):.1f} MB -> depois {mb(slim):.1f} MB ({mb(orders) / mb(slim):.1f}x menor)")
print("mesmos valores nas colunas inteiras?", (slim["qty"].astype("int64") == orders["qty"]).all())

# 4. leitura do CSV: dizer os tipos na ENTRADA é melhor do que converter depois
buffer = io.StringIO()
orders.to_csv(buffer, index=False)
text = buffer.getvalue()
print(f"\nCSV de {len(text) / 1e6:.1f} MB em texto")


def read(**kwargs):
    start = time.perf_counter()
    frame = pd.read_csv(io.StringIO(text), **kwargs)
    return frame, (time.perf_counter() - start) * 1e3


types = {"product": "category", "status": "category", "qty": "uint8", "customer_id": "uint16", "order_id": "uint32"}
plain, t_plain = read()
default, t_default = read(parse_dates=["date"])
typed, t_typed = read(dtype=types, parse_dates=["date"])
lean, t_lean = read(dtype=types, parse_dates=["date"], usecols=["order_id", "customer_id", "date", "product", "qty", "status", "total"])
arrow, t_arrow = read(engine="pyarrow")
print(f"read_csv sem opções          : {t_plain:6.0f} ms | {mb(plain):6.1f} MB | a coluna date fica como TEXTO ({plain['date'].dtype})")
print(f"+ parse_dates                : {t_default:6.0f} ms | {mb(default):6.1f} MB")
print(f"+ dtype por coluna           : {t_typed:6.0f} ms | {mb(typed):6.1f} MB")
print(f"+ usecols (7 de 8 colunas)   : {t_lean:6.0f} ms | {mb(lean):6.1f} MB")
print(f"engine='pyarrow'             : {t_arrow:6.0f} ms | {mb(arrow):6.1f} MB (mais rápido, mas com menos opções)")

# 5. datas: guarde como datetime, não como texto
as_text = orders["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
print(f"\ndatas como texto {mb(as_text):.1f} MB | como datetime64[us] {mb(orders['date']):.1f} MB | resolução: {orders['date'].dtype}")
start = time.perf_counter()
parsed = pd.to_datetime(as_text, format="%Y-%m-%d %H:%M:%S")
t_fmt = (time.perf_counter() - start) * 1e3
print(f"to_datetime com format= : {t_fmt:6.1f} ms | idêntico? {parsed.equals(orders['date'])}")

# 6. valores ausentes: o que cada tipo permite
print("\nint64 não tem ausente (vira float64):", pd.Series([1, None]).dtype,
      "| 'Int64' tem:", pd.Series([1, None], dtype="Int64").dtype,
      "| bool com ausente:", pd.Series([True, None], dtype="boolean").tolist())

# 7. índice também ocupa memória
idx = pd.DataFrame({"v": range(1_000_000)})
print(f"\nRangeIndex de 1 milhão de linhas: {idx.index.memory_usage() } bytes | Index de int64: "
      f"{pd.Index(np.arange(1_000_000)).memory_usage() / 1e6:.1f} MB")
