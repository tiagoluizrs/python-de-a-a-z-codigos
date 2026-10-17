"""Vetorização: tirar o laço do Python. Quanto custa, quanto ganha, onde não ganha."""
import math
import statistics
import time

import numpy as np

N = 1_000_000
rng = np.random.default_rng(42)
a = rng.random(N)
b = rng.random(N)
la, lb = a.tolist(), b.tolist()


def best(fn, repeat=5):
    """Melhor tempo (ms) de `repeat` execuções: a menor medida é a menos contaminada por ruído."""
    times = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        times.append((time.perf_counter() - start) * 1e3)
    return min(times)


def row(label, ms, base=None):
    extra = f"  ({base / ms:7.1f}x mais rápido)" if base else ""
    print(f"  {label:<44} {ms:9.3f} ms{extra}")


# 1. a mesma conta, quatro jeitos: soma de a*b + 1
print(f"1. sum(a*b + 1) com {N:,} números")
loop = best(lambda: sum(x * y + 1 for x, y in zip(la, lb)), 3)
row("Python puro (gerador sobre listas)", loop)
row("math.fsum (exata, ainda em Python)", best(lambda: math.fsum(x * y + 1 for x, y in zip(la, lb)), 3))
row("NumPy vetorizado: (a * b + 1).sum()", best(lambda: (a * b + 1).sum()), loop)
row("NumPy com np.dot(a, b) + N (menos memória)", best(lambda: np.dot(a, b) + N), loop)

# 2. o laço NA MÃO sobre ndarray é PIOR que sobre lista (cada a[i] cria um objeto novo)
print("\n2. laço Python sobre o ndarray (o erro mais comum)")
row("for x in lista (floats nativos)", best(lambda: sum(x for x in la), 3))
row("for x in ndarray (um np.float64 por item)", best(lambda: sum(x for x in a), 3))
row("a.sum()", best(lambda: a.sum()))

# 3. np.vectorize é açúcar de sintaxe, NÃO velocidade
print("\n3. np.vectorize x ufunc de verdade")


def clip_py(x):
    return x if x < 0.5 else 0.5


vec = np.vectorize(clip_py)
t_vec = best(lambda: vec(a), 3)
row("np.vectorize(função Python)", t_vec)
row("[clip_py(x) for x in lista]", best(lambda: [clip_py(x) for x in la], 3))
row("np.minimum(a, 0.5)  (ufunc, em C)", best(lambda: np.minimum(a, 0.5)), t_vec)
row("np.clip(a, None, 0.5)", best(lambda: np.clip(a, None, 0.5)), t_vec)

# 4. temporários: cada operação aloca um array novo; out= reutiliza memória
print("\n4. temporários e out=")
buffer = np.empty_like(a)


def with_temps():
    return a * 2.0 + b * 3.0 - 1.0                     # 5 arrays temporários de 8 MB


def with_out():
    np.multiply(a, 2.0, out=buffer)
    buffer.__iadd__(b * 3.0)
    np.subtract(buffer, 1.0, out=buffer)
    return buffer


t_temp = best(with_temps)
row("a*2 + b*3 - 1 (alocando temporários)", t_temp)
row("com out= e operadores in-place", best(with_out), t_temp)
print("  mesmo resultado?", np.allclose(with_temps(), with_out()))

# 5. condicional vetorizado: where, select, máscaras
print("\n5. condição sem if")
vals = rng.normal(size=N)
t_if = best(lambda: [x if x > 0 else 0.0 for x in vals.tolist()], 3)
row("lista com if/else", t_if)
row("np.where(v > 0, v, 0.0)", best(lambda: np.where(vals > 0, vals, 0.0)), t_if)
row("np.maximum(v, 0.0)  (a forma idiomática)", best(lambda: np.maximum(vals, 0.0)), t_if)

# 6. ufunc methods: reduce, accumulate, outer, at
x = np.arange(1, 6)
print("\n6. métodos das ufuncs")
print("  add.reduce    :", np.add.reduce(x), "(= sum)")
print("  add.accumulate:", np.add.accumulate(x), "(= cumsum)")
print("  multiply.accumulate:", np.multiply.accumulate(x), "(fatoriais)")
print("  multiply.outer:", np.multiply.outer(x[:3], x[:3]).tolist(), "(tabuada)")
counts = np.zeros(4, dtype=np.int64)
np.add.at(counts, [0, 1, 1, 3, 3, 3], 1)
print("  add.at (índices repetidos):", counts, "| counts[[0,1,1]] += 1 daria", end=" ")
wrong = np.zeros(4, dtype=np.int64)
wrong[[0, 1, 1, 3, 3, 3]] += 1
print(wrong, "(só conta uma vez)")

# 7. onde NÃO vale: pouco dado, e conta que depende do passo anterior
print("\n7. onde a vetorização não ajuda")
small_l, small_a = [1.0, 2.0, 3.0], np.array([1.0, 2.0, 3.0])
us_list = best(lambda: [sum(small_l) for _ in range(10_000)]) / 10_000 * 1e3
us_array = best(lambda: [small_a.sum() for _ in range(10_000)]) / 10_000 * 1e3
print(f"  soma de 3 itens: lista {us_list:.2f} µs | ndarray {us_array:.2f} µs ({us_array / us_list:.1f}x MAIS LENTO)")


def recurrence(n):                                     # x[i] depende de x[i-1]: laço inevitável
    x = 0.5
    for _ in range(n):
        x = 3.9 * x * (1 - x)
    return x


row("mapa logístico, 1 milhão de passos", best(lambda: recurrence(N), 2))
print("  (dependência entre passos: não dá para vetorizar; a saída é Numba/Cython/C, fora deste capítulo)")

# 8. estatística: statistics (exata, lenta) x NumPy (rápida, em float64)
print("\n8. média e desvio padrão")
row("statistics.fmean", best(lambda: statistics.fmean(la), 3))
row("np.mean", best(lambda: a.mean()))
print("  fmean:", statistics.fmean(la), "| np.mean:", a.mean())
