"""Copy-on-Write: no pandas 3, o que você DERIVA de um DataFrame nunca altera a origem."""
import time
import warnings

import numpy as np
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3], "b": [10.0, 20.0, 30.0]})

# 1. uma seleção é SEMPRE independente: escrever nela não toca o original
subset = df[df["a"] > 1]
subset.loc[subset.index[0], "b"] = 999.0
print("subset alterado:", subset["b"].tolist(), "| original intacto:", df["b"].tolist())

# 2. o mesmo para uma coluna tirada do DataFrame
col = df["a"]
col.iloc[0] = 100
print("coluna alterada:", col.tolist(), "| original intacto:", df["a"].tolist())

# 3. mas CoW NÃO impede que você altere o PRÓPRIO objeto que recebeu: `frame["a"] = ...` muda quem chamou
def clamp_in_place(frame):
    frame["a"] = frame["a"].clip(upper=2)
    return frame


def clamp_pure(frame):
    return frame.assign(a=frame["a"].clip(upper=2))


clamp_pure(df)
print("\nclamp_pure(df)   -> original:", df["a"].tolist(), "(assign devolve um objeto novo)")
mine = pd.DataFrame({"a": [1, 5, 9]})
clamp_in_place(mine)
print("clamp_in_place(mine) -> mine agora:", mine["a"].tolist(), "(o objeto recebido É o mesmo: foi alterado)")

# 4. atribuição ENCADEADA nunca funcionou direito; agora avisa e não faz nada
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    df["a"][0] = 555
print("\ndf['a'][0] = 555 ->", df["a"].tolist(), "| aviso:", caught[0].category.__name__)
df.loc[0, "a"] = 555                                         # a forma certa: UM .loc com linha e coluna
print("df.loc[0, 'a'] = 555 ->", df["a"].tolist())

# 5. a cópia é PREGUIÇOSA: selecionar colunas, renomear e fatiar não copiam os dados até alguém escrever
big = pd.DataFrame(np.random.default_rng(0).random((2_000_000, 4)), columns=list("abcd"))


def shares(origin, derived, origin_col="a", derived_col=None):
    """A coluna `derived_col` do derivado usa a MESMA memória da coluna `origin_col` da origem?"""
    return np.shares_memory(origin[origin_col].to_numpy(), derived[derived_col or origin_col].to_numpy())


print(f"\nDataFrame de {big.memory_usage().sum() / 1e6:.0f} MB:")
for label, make in [("big[['a','b']]", lambda: big[["a", "b"]]), ("big.rename(...)", lambda: big.rename(columns={"a": "x"})),
                    ("big.iloc[:1000]", lambda: big.iloc[:1000]), ("big.copy(deep=False)", lambda: big.copy(deep=False)),
                    ("big[big.a > .5]", lambda: big[big["a"] > 0.5]), ("big.copy()", lambda: big.copy())]:
    start = time.perf_counter()
    other = make()
    ms = (time.perf_counter() - start) * 1e3
    derived_col = "x" if "rename" in label else "a"
    print(f"  {label:<22} {ms:7.2f} ms | compartilha os dados com big? {shares(big, other, "a", derived_col)}")

view = big[["a", "b"]]
view.loc[0, "a"] = -1.0
print("\napós escrever em view['a']: a compartilha?", shares(big, view), "| b (não escrita) ainda compartilha?", shares(big, view, "b"))
print("original intacto?", big.loc[0, "a"] != -1.0)

# 6. arrays "emprestados" do pandas são somente leitura (para o CoW poder proteger)
arr = big["a"].to_numpy()
print("\nto_numpy() é gravável?", arr.flags.writeable, "| to_numpy(copy=True) é gravável?", big["a"].to_numpy(copy=True).flags.writeable)

# 7. o estilo moderno: encadear métodos, sem variáveis intermediárias nem inplace=True
result = (
    pd.DataFrame({"city": ["Recife", "Recife", "Salvador"], "total": [10.0, 20.0, 5.0]})
    .query("total > 5")
    .groupby("city", as_index=False)
    .agg(total=("total", "sum"))
    .sort_values("total", ascending=False)
)
print("\nencadeamento:\n", result.to_string())
