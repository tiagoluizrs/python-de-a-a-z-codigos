"""Broadcasting: operar sobre formas diferentes sem copiar e sem laço."""
import time

import numpy as np

# 1. a regra: alinhe as formas pela DIREITA; cada par de eixos precisa ser igual ou ter um 1
a = np.arange(6).reshape(2, 3)                  # (2, 3)
row = np.array([10, 20, 30])                     # (3,)   -> vira (1, 3) -> (2, 3)
col = np.array([[100], [200]])                   # (2, 1) -> (2, 3)
print("(2,3) + (3,)  =\n", a + row)
print("(2,3) + (2,1) =\n", a + col)
print("(2,1) + (1,3) = (2,3):\n", col + row.reshape(1, 3))

# 2. o erro quando não casa
try:
    a + np.array([1, 2])                         # (2,3) + (2,): o 3 não casa com o 2
except ValueError as error:
    print("\n(2,3) + (2,) ->", error)

# 3. broadcasting NÃO copia: os dados ficam onde estão, o stride do eixo repetido é 0
view = np.broadcast_to(np.array([1, 2, 3]), (1000, 3))
print("\nbroadcast_to (1000,3): strides", view.strides, "| nbytes lógico", view.nbytes,
      "| bytes reais no bloco", view.base.nbytes if view.base is not None else "?")
print("somente leitura?", not view.flags.writeable, "(escrever em posições que repetem seria ambíguo)")

# 4. o caso clássico: distâncias entre todos os pares de pontos, sem laço
rng = np.random.default_rng(7)
points = rng.random((2000, 3))
diff = points[:, None, :] - points[None, :, :]   # (2000,1,3) - (1,2000,3) = (2000,2000,3)
dist = np.sqrt((diff ** 2).sum(axis=-1))
print("\ndistâncias:", dist.shape, "| diagonal zero?", np.allclose(np.diag(dist), 0),
      "| simétrica?", np.allclose(dist, dist.T))
print(f"o intermediário (2000,2000,3) float64 pesa {diff.nbytes / 1e6:.0f} MB (o preço do atalho)")

# 5. a alternativa que não monta o cubo: |x - y|^2 = |x|^2 + |y|^2 - 2 x.y
sq = (points ** 2).sum(axis=1)
dist2 = np.sqrt(np.maximum(sq[:, None] + sq[None, :] - 2 * points @ points.T, 0))
print("mesma resposta sem o cubo?", np.allclose(dist, dist2, atol=1e-6))


def best(fn, repeat=3):
    out = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        out.append((time.perf_counter() - start) * 1e3)
    return min(out)


def python_loop(pts):
    n = len(pts)
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            out[i][j] = sum((pts[i][k] - pts[j][k]) ** 2 for k in range(3)) ** 0.5
    return out


small = points[:300]
t_loop = best(lambda: python_loop(small.tolist()), 1)
t_cube = best(lambda: np.sqrt(((small[:, None, :] - small[None, :, :]) ** 2).sum(-1)))
print(f"\n300 pontos  | laço Python: {t_loop:8.1f} ms | broadcasting: {t_cube:6.2f} ms ({t_loop / t_cube:.0f}x)")
t_cube = best(lambda: np.sqrt(((points[:, None, :] - points[None, :, :]) ** 2).sum(-1)))
t_gemm = best(lambda: np.sqrt(np.maximum(sq[:, None] + sq[None, :] - 2 * points @ points.T, 0)))
print(f"2000 pontos | cubo (3 eixos): {t_cube:8.1f} ms | produto de matrizes: {t_gemm:6.2f} ms ({t_cube / t_gemm:.0f}x)")

# 6. a pegadinha do (n,) contra (n,1): um eixo a mais vira uma matriz sem aviso
x = np.array([1.0, 2.0, 3.0])                    # (3,)
y = np.array([[10.0], [20.0], [30.0]])           # (3, 1)
print("\n(3,) + (3,1) =", (x + y).shape, "(uma MATRIZ 3x3, não 3 somas)")
print("com keepdims=True a média mantém o eixo e o broadcasting acerta:")
m = np.arange(6.0).reshape(2, 3)
print("  m - m.mean(axis=1)               ->", end=" ")
try:
    m - m.mean(axis=1)
except ValueError as error:
    print("ValueError:", str(error)[:55])
print("  m - m.mean(axis=1, keepdims=True) ->", (m - m.mean(axis=1, keepdims=True)).tolist())

# 7. normalizar colunas e produto externo, os dois usos do dia a dia
data = rng.normal(loc=[0, 50, 1000], scale=[1, 10, 200], size=(10_000, 3))
z = (data - data.mean(axis=0)) / data.std(axis=0)
print("\nz-score por coluna: |média| máxima", f"{np.abs(z.mean(axis=0)).max():.1e}", "| desvio", z.std(axis=0).round(6))
table = np.arange(1, 4)[:, None] * np.arange(1, 4)[None, :]
print("tabuada 3x3 por broadcasting:", table.tolist())
