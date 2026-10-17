"""Números aleatórios com Generator: reprodutibilidade e execuções paralelas independentes."""
import random
import time

import numpy as np

# 1. a API moderna: Generator, criado explicitamente (sem estado global escondido)
rng = np.random.default_rng(seed=2026)
print("random      :", rng.random(3).round(4))
print("integers    :", rng.integers(1, 7, size=10), "(o limite superior NÃO entra)")
print("normal      :", rng.normal(loc=100, scale=15, size=3).round(2))
print("choice      :", rng.choice(["a", "b", "c"], size=5, p=[0.7, 0.2, 0.1]))
print("sem reposição:", rng.choice(10, size=5, replace=False), "| permutation:", rng.permutation(5))
deck = np.arange(5)
rng.shuffle(deck)
print("shuffle (in-place):", deck)

# 2. mesma semente, mesma sequência (e semente diferente, outra)
a = np.random.default_rng(1).random(3)
b = np.random.default_rng(1).random(3)
c = np.random.default_rng(2).random(3)
print("\nsemente 1 duas vezes igual?", np.array_equal(a, b), "| semente 2 diferente?", not np.array_equal(a, c))

# 3. a API legada (np.random.seed / np.random.rand) usa um estado GLOBAL: evite
np.random.seed(0)
x1 = np.random.rand(2)
np.random.seed(0)
x2 = np.random.rand(2)
print("API legada reproduz, mas qualquer biblioteca que a use mexe no mesmo estado:", np.array_equal(x1, x2))

# 4. paralelismo: NUNCA a mesma semente em todos os workers (todos sorteiam os mesmos números)
same = [np.random.default_rng(42).random(2).round(3).tolist() for _ in range(3)]
print("\n3 workers com a MESMA semente:", same, "(números repetidos: estatística falsa)")
children = np.random.SeedSequence(42).spawn(3)
independent = [np.random.default_rng(child).random(2).round(3).tolist() for child in children]
print("3 workers com SeedSequence.spawn:", independent, "(fluxos independentes e reproduzíveis)")

# 5. estado salvo e restaurado (retomar uma simulação)
rng = np.random.default_rng(5)
rng.random(100)
state = rng.bit_generator.state
first = rng.random(3)
rng.bit_generator.state = state
print("\nretomar do estado salvo repete a sequência?", np.array_equal(first, rng.random(3)))

# 6. velocidade contra o módulo random da biblioteca padrão
N = 1_000_000
start = time.perf_counter()
[random.random() for _ in range(N)]
t_std = (time.perf_counter() - start) * 1e3
rng = np.random.default_rng(0)
start = time.perf_counter()
rng.random(N)
t_np = (time.perf_counter() - start) * 1e3
print(f"\n{N:,} números: random.random em laço {t_std:6.1f} ms | rng.random(N) {t_np:5.2f} ms ({t_std / t_np:.0f}x)")

# 7. simulação de Monte Carlo: estimar pi sem laço
points = np.random.default_rng(11).random((5_000_000, 2))
inside = ((points ** 2).sum(axis=1) <= 1.0).mean()
print(f"pi ~ {4 * inside:.4f} com 5 milhões de pontos (erro típico ~ 1/raiz(n) = {1 / 5_000_000 ** 0.5:.4f})")

# 8. aleatório NÃO é seguro: para senhas e tokens use secrets (Capítulo 8 do Volume 3)
print("\nGenerator é para ciência e simulação, previsível a partir do estado; segredos: secrets.token_urlsafe()")
