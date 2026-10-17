"""Defesa em profundidade: rodar a regex em outro processo com timeout.

O módulo re não tem timeout próprio e não solta o controle enquanto
casa: uma thread não pode ser interrompida. Um processo pode.
"""
import multiprocessing as mp
import re
import time


def _worker(pattern: str, text: str, queue) -> None:
    queue.put(bool(re.search(pattern, text)))


def search_with_timeout(pattern: str, text: str, seconds: float):
    """Devolve True/False, ou None se estourar o tempo."""
    queue = mp.Queue()
    proc = mp.Process(target=_worker, args=(pattern, text, queue))
    proc.start()
    proc.join(seconds)
    if proc.is_alive():
        proc.terminate()
        proc.join()
        return None
    return queue.get()


if __name__ == "__main__":
    evil = r"(a+)+$"
    start = time.perf_counter()
    print(search_with_timeout(evil, "a" * 40 + "!", 0.5))
    print(f"{time.perf_counter() - start:.2f}s")
    print(search_with_timeout(evil, "a" * 40, 0.5))
