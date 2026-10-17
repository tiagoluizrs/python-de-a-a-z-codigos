"""Dividir, processar em paralelo e combinar: contagem de palavras."""
import collections
import multiprocessing as mp
import time

import tasks

TEXT = ("o rato roeu a roupa do rei de roma " * 2_000).strip()

if __name__ == "__main__":
    texts = [TEXT] * 40
    start = time.perf_counter()
    sequential = collections.Counter()
    for text in texts:
        sequential += tasks.count_words(text)
    t_seq = time.perf_counter() - start

    start = time.perf_counter()
    with mp.Pool(4) as pool:
        partials = pool.map(tasks.count_words, texts)
    total = sum(partials, collections.Counter())
    t_par = time.perf_counter() - start
    print("iguais:", total == sequential, "| 'rato':", total["rato"])
    print(f"sequencial {t_seq * 1e3:.0f} ms | 4 processos {t_par * 1e3:.0f} ms (a tarefa é curta: o custo de partida e de cópia domina)")
