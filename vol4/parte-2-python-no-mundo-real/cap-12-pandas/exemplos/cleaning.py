"""Limpeza de dados: a planilha como ela chega, passo a passo."""
import numpy as np
import pandas as pd

from sample_data import make_dirty_orders

raw = make_dirty_orders()
print("como chegou:\n", raw.to_string())
print("tipos:", raw.dtypes.astype(str).unique().tolist(), "(tudo texto)")

# 1. nomes de colunas: um padrão só (snake_case), antes de qualquer outra coisa
df = raw.rename(columns=lambda c: c.strip().lower().replace(" ", "_"))
print("\ncolunas:", df.columns.tolist())

# 2. texto: espaços, caixa, vazio que é ausente
df["customer"] = df["customer"].str.strip().str.title().replace("", np.nan)
df["status"] = df["status"].str.lower().astype("category")
print("\nclientes:", df["customer"].tolist())
print("(o '  ' virou '' e depois NaN; 'bruno LIMA' -> 'Bruno Lima')")

# 3. números em texto: separador brasileiro, símbolo de moeda, lixo
def parse_money(series: pd.Series) -> pd.Series:
    cleaned = (series.str.replace("R$", "", regex=False).str.strip()
               .str.replace(".", "", regex=False).str.replace(",", ".", regex=False))
    return pd.to_numeric(cleaned, errors="coerce")


df["amount"] = parse_money(df["amount"])
print("\nvalores:", df["amount"].tolist(), "| 'abc' virou NaN (errors='coerce'), nada de exceção no meio do arquivo")

# 4. datas em dois formatos: tentar o primeiro, depois o segundo, e SÓ ENTÃO coerce
first = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="coerce")
second = pd.to_datetime(df["date"], format="%d/%m/%Y", errors="coerce")
df["date"] = first.fillna(second)
print("datas:", df["date"].dt.strftime("%Y-%m-%d").tolist(), "| 'não sei' virou NaT")

# 5. id: texto -> inteiro que aceita ausente
df["order_id"] = pd.to_numeric(df["order_id"], errors="coerce").astype("Int64")
print("ids:", df["order_id"].tolist())

# 6. duplicatas: ver ANTES de apagar
print("\nlinhas duplicadas (todas as colunas):", int(df.duplicated().sum()), "| pelo id:", int(df.duplicated("order_id", keep=False).sum()), "envolvidas")
print(df[df.duplicated("order_id", keep=False)].to_string())
clean = df.drop_duplicates()

# 7. ausentes: quantos e o que fazer (descartar? preencher? marcar?)
print("\nausentes por coluna:", clean.isna().sum().to_dict())
valid = clean.dropna(subset=["order_id", "customer", "amount", "date"])
print(f"dropna nas colunas essenciais: {len(clean)} -> {len(valid)} linhas")
print("o relatório do que foi descartado:\n", clean.loc[~clean.index.isin(valid.index), ["order_id", "customer", "amount", "date"]].to_string())

# 8. validar regras de negócio com asserções legíveis
assert (valid["amount"] > 0).all(), "valor não positivo"
assert valid["order_id"].is_unique, "id repetido"
print("\nregras de negócio ok | tipos finais:", valid.dtypes.astype(str).to_dict())

# 9. outliers: o intervalo interquartil, sem apagar nada às cegas
x = pd.Series([10, 12, 11, 13, 12, 400, 11, 9])
q1, q3 = x.quantile([0.25, 0.75])
iqr = q3 - q1
mask = (x < q1 - 1.5 * iqr) | (x > q3 + 1.5 * iqr)
print("\noutliers pelo IQR:", x[mask].tolist(), "| winsorize com clip:", x.clip(q1 - 1.5 * iqr, q3 + 1.5 * iqr).tolist())
