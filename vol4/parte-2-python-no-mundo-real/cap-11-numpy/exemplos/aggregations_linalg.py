"""Agregações por eixo, NaN, precisão numérica e álgebra linear."""
import math
import time

import numpy as np

m = np.arange(12, dtype=float).reshape(3, 4)
print("m =\n", m)

# 1. axis: o eixo que DESAPARECE
print("\nsum(axis=0) =", m.sum(axis=0), "(colapsa as linhas: um valor por coluna)")
print("sum(axis=1) =", m.sum(axis=1), "(um valor por linha)")
print("sum() total =", m.sum(), "| mean(axis=(0, 1)) =", m.mean(axis=(0, 1)))
print("keepdims   :", m.sum(axis=1, keepdims=True).shape, "(mantém o eixo, para broadcasting)")
print("cumsum     :", np.cumsum(m[0]), "| diff:", np.diff(m[0]), "| ptp:", np.ptp(m, axis=1))
print("percentil  :", np.percentile(m, [25, 50, 75]), "| mediana:", np.median(m), "| std (ddof=1):", m.std(ddof=1).round(3))

# 2. NaN: contagioso, e NaN != NaN
v = np.array([1.0, np.nan, 3.0])
print("\nsum com NaN  :", v.sum(), "| nansum:", np.nansum(v), "| nanmean:", np.nanmean(v))
print("nan == nan   :", np.nan == np.nan, "| isnan:", np.isnan(v), "| nan in lista:", np.nan in [np.nan])
print("max com NaN  :", v.max(), "| nanmax:", np.nanmax(v), "| argmax (NaN ganha!):", v.argmax())
print("None vira NaN? array([1.0, None], dtype=float):", np.array([1.0, None], dtype=float))

# 3. comparar floats: nunca ==
x = np.array([0.1 + 0.2])
print("\n0.1+0.2 == 0.3:", bool((x == 0.3)[0]), "| np.isclose:", bool(np.isclose(x, 0.3)[0]),
      "| allclose(rtol=1e-5):", np.allclose(x, 0.3))
print("isclose: |a-b| <= atol + rtol*|b|. Comparando com zero só o atol conta (padrão 1e-8):",
      np.isclose(1e-12, 0.0), np.isclose(1e-6, 0.0), "| com atol=0:", np.isclose(1e-12, 0.0, atol=0))

# 4. soma de floats: o NumPy soma em pares (pairwise) e erra menos que o laço ingênuo
rng = np.random.default_rng(1)
data = rng.random(10_000_000).astype(np.float32)
exact = math.fsum(data.astype(np.float64).tolist())
naive = np.float32(0)
for chunk in np.array_split(data, 10_000):         # laço sobre pedaços, soma 'sequencial' de float32
    naive += chunk.sum(dtype=np.float32)
print("\nsoma de 10 milhões de float32 (exata =", f"{exact:.1f})")
print("  data.sum() (pairwise, float32)       erro:", f"{abs(float(data.sum()) - exact):10.4f}")
print("  data.sum(dtype=float64)              erro:", f"{abs(float(data.sum(dtype=np.float64)) - exact):10.4f}")
print("  acumulador float32 em pedaços        erro:", f"{abs(float(naive) - exact):10.4f}")

# 5. álgebra linear
A = np.array([[3.0, 1.0], [1.0, 2.0]])
b = np.array([9.0, 8.0])
print("\nA @ A =", (A @ A).tolist(), "| A * A (elemento a elemento) =", (A * A).tolist())
sol = np.linalg.solve(A, b)
print("solve(A, b) =", sol, "| confere:", np.allclose(A @ sol, b))
print("inv(A) @ b dá o mesmo, mas é mais lento e menos preciso; use solve:", np.linalg.inv(A) @ b)
print("det =", round(np.linalg.det(A), 6), "| autovalores:", np.linalg.eigvalsh(A).round(4), "| norma:", np.linalg.norm(b).round(4))
print("matriz singular:", end=" ")
try:
    np.linalg.solve(np.array([[1.0, 2.0], [2.0, 4.0]]), b)
except np.linalg.LinAlgError as error:
    print("LinAlgError:", error)

# 6. einsum: a notação de índices para somas de produtos
P = rng.random((50, 30))
Q = rng.random((30, 20))
print("\neinsum('ij,jk->ik') == P @ Q:", np.allclose(np.einsum("ij,jk->ik", P, Q), P @ Q))
print("einsum('ii', A) (traço):", np.einsum("ii", A), "| 'ij->ji' (transposta):", np.einsum("ij->ji", A).tolist())
batch = rng.random((8, 4, 3))
print("produto escalar de cada par do lote:", np.einsum("bij,bij->b", batch, batch).shape)

# 7. produto de matrizes: BLAS contra laço Python
n = 200
X = rng.random((n, n))
Y = rng.random((n, n))


def matmul_py(x, y):
    xl, yt = x.tolist(), y.T.tolist()
    return [[sum(p * q for p, q in zip(row, col)) for col in yt] for row in xl]


start = time.perf_counter()
matmul_py(X, Y)
t_py = (time.perf_counter() - start) * 1e3
start = time.perf_counter()
for _ in range(20):
    X @ Y
t_np = (time.perf_counter() - start) * 1e3 / 20
print(f"\nmultiplicar duas matrizes {n}x{n}: Python {t_py:8.1f} ms | X @ Y {t_np:6.3f} ms ({t_py / t_np:,.0f}x)")

# 8. ordem de memória: somar por linha x por coluna num array C-contíguo
big = rng.random((6000, 6000))                      # 288 MB; a ordem C guarda cada linha junta
for name, fn in [("soma de cada LINHA  (contígua)", lambda: big.sum(axis=1)),
                 ("soma de cada COLUNA (salta)", lambda: big.sum(axis=0)),
                 ("percorrer COLUNA a COLUNA a[:, j]", lambda: [big[:, j].sum() for j in range(0, 6000, 6)]),
                 ("percorrer LINHA a LINHA a[i]", lambda: [big[i].sum() for i in range(0, 6000, 6)])]:
    times = []
    for _ in range(3):
        start = time.perf_counter()
        fn()
        times.append(time.perf_counter() - start)
    print(f"  {name:<36} {min(times) * 1e3:8.1f} ms")
print("  (as duas últimas leem 1/6 dos dados; compare uma com a outra)")
