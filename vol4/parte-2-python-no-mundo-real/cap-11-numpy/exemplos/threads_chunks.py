"""NumPy solta o GIL: threads ajudam. Pedaços, janelas deslizantes e problemas reais sem laço."""
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def best(fn, repeat=3):
    out = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        out.append((time.perf_counter() - start) * 1e3)
    return min(out)


rng = np.random.default_rng(9)

# 1. trabalho numérico em C solta o GIL: threads de verdade, sem processos (Capítulos 14 e 19 do Volume 3)
x = rng.random(16_000_000)
chunks = np.array_split(x, 16)


def heavy(chunk):
    return np.sin(chunk) ** 2 + np.cos(chunk) ** 2 + np.sqrt(chunk)


print("1. 16 milhões de senos/cossenos/raízes, em 16 pedaços")
t1 = best(lambda: [heavy(c) for c in chunks], 2)
print(f"  1 thread (sequencial)  {t1:8.1f} ms")
for workers in (2, 4, 8):
    with ThreadPoolExecutor(workers) as pool:
        t = best(lambda: list(pool.map(heavy, chunks)), 2)
    print(f"  {workers} threads             {t:8.1f} ms  ({t1 / t:4.1f}x)")

# 2. e o trabalho que NÃO solta o GIL fica preso
print("\n2. a mesma ideia com um laço Python por pedaço (o GIL segura)")
py_chunks = [c[:200_000].tolist() for c in chunks[:8]]


def python_work(items):
    return sum(v * v for v in items)


t1 = best(lambda: [python_work(c) for c in py_chunks], 2)
with ThreadPoolExecutor(8) as pool:
    t8 = best(lambda: list(pool.map(python_work, py_chunks)), 2)
print(f"  sequencial {t1:7.1f} ms | 8 threads {t8:7.1f} ms ({t1 / t8:.1f}x: sem ganho no 3.15 com GIL)")

# 3. janelas deslizantes: média móvel de três formas
series = rng.random(2_000_000)
w = 50
loop_part = series[:50_000].tolist()
t_loop = best(lambda: [sum(loop_part[i:i + w]) / w for i in range(len(loop_part) - w + 1)], 1) * (len(series) / 50_000)
print("\n3. média móvel (janela 50) de 2 milhões de pontos")
print(f"  laço Python com fatias         ~{t_loop:9.0f} ms (extrapolado de 50 mil pontos)")
t_conv = best(lambda: np.convolve(series, np.ones(w) / w, mode="valid"), 2)
t_cs = best(lambda: (lambda c: (c[w:] - c[:-w]) / w)(np.cumsum(series)))
t_view = best(lambda: sliding_window_view(series, w).mean(axis=1), 2)
print(f"  np.convolve                    {t_conv:9.1f} ms")
print(f"  cumsum (diferença de somas)    {t_cs:9.1f} ms")
print(f"  sliding_window_view().mean     {t_view:9.1f} ms  (uma VIEW 2M x 50 sem copiar; o mean percorre 100M valores)")
c = np.cumsum(series)
fast = (c[w:] - c[:-w]) / w
print("  mesmas respostas?", np.allclose(fast, np.convolve(series, np.ones(w) / w, "valid")[1:], atol=1e-9),
      "| view compartilha memória?", np.shares_memory(sliding_window_view(series, w), series))

# 4. pedaços: temporários grandes saem do cache; trabalhar em blocos pode ganhar
big = rng.random(30_000_000)
out = np.empty_like(big)


def whole():
    return np.sqrt(big * 2.0 + 1.0) * 0.5


def blocked(size=1 << 17):
    for i in range(0, big.size, size):
        block = out[i:i + size]
        np.multiply(big[i:i + size], 2.0, out=block)
        np.add(block, 1.0, out=block)
        np.sqrt(block, out=block)
        np.multiply(block, 0.5, out=block)
    return out


t_whole = best(whole)
t_block = best(blocked)
print(f"\n4. 30 milhões de itens: expressão inteira {t_whole:7.1f} ms | em blocos de 1 MB com out= {t_block:7.1f} ms")
print("   mesma resposta?", np.allclose(whole(), blocked()))

# 5. problema real sem laços: o Jogo da Vida em uma grade, com np.roll
def life_step(grid: np.ndarray) -> np.ndarray:
    neighbors = sum(np.roll(np.roll(grid, dy, 0), dx, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) - grid
    return ((neighbors == 3) | ((grid == 1) & (neighbors == 2))).astype(grid.dtype)


glider = np.zeros((10, 10), dtype=np.uint8)
glider[0, 1] = glider[1, 2] = glider[2, 0] = glider[2, 1] = glider[2, 2] = 1
g = glider
for _ in range(4):
    g = life_step(g)
print("\n5. planador depois de 4 passos andou uma casa na diagonal?", np.array_equal(g, np.roll(glider, (1, 1), (0, 1))))
grid = (rng.random((1000, 1000)) < 0.3).astype(np.uint8)
print(f"   passo em uma grade de 1 milhão de células: {best(lambda: life_step(grid)):.1f} ms")

# 6. imagem é só um array uint8: cinza, brilho (com cuidado com o estouro) e recorte
img = rng.integers(0, 256, size=(1080, 1920, 3), dtype=np.uint8)
gray = (img @ np.array([0.299, 0.587, 0.114])).astype(np.uint8)
bright_wrong = img + 100                                          # uint8 dá a volta (255 + 100 = 99)
bright_ok = np.clip(img.astype(np.int16) + 100, 0, 255).astype(np.uint8)
print(f"\n6. imagem 1080p: {img.nbytes / 1e6:.1f} MB | cinza {gray.shape} em {best(lambda: (img @ np.array([0.299, 0.587, 0.114])).astype(np.uint8)):.1f} ms")
print("   brilho errado (estoura):", (np.array([200], dtype=np.uint8) + 100)[0], "| certo (clip):", np.clip(np.int16(200) + 100, 0, 255),
      "| pixels diferentes nas duas versões:", int((bright_wrong != bright_ok).sum()))
crop = img[100:500, 200:700]
print("   recorte é view?", np.shares_memory(img, crop), "(o OpenCV do Apêndice A deste volume usa exatamente esse array)")
