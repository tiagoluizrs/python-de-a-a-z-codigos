"""Processos não compartilham memória: tudo que viaja é copiado (pickle)."""
import multiprocessing as mp
import pickle
import time


def pickle_cost():
    for size in (10_000, 1_000_000):
        data = list(range(size))
        start = time.perf_counter()
        blob = pickle.dumps(data)
        pickle.loads(blob)
        print(f"  pickle ida e volta de {size:>9,} inteiros: {len(blob) / 1e6:5.2f} MB em {(time.perf_counter() - start) * 1e3:6.1f} ms")


def local_function(x):
    return x


if __name__ == "__main__":
    q = mp.Queue()
    p = mp.Process(target=q.put, args=("olá do filho",))
    p.start()
    print("Queue:", q.get(timeout=5))
    p.join()

    a, b = mp.Pipe()
    a.send({"chave": [1, 2, 3]})
    print("Pipe :", b.recv())

    print("o que viaja é uma CÓPIA:")
    pickle_cost()

    try:
        with mp.Pool(2) as pool:
            pool.map(lambda x: x, [1])
    except Exception as error:
        print(f"  lambda: {type(error).__name__}: {str(error)[:55]}...")
    with mp.Pool(2) as pool:
        print("  função de módulo: funciona ->", pool.map(local_function, [1]))
