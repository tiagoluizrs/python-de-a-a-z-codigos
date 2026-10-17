"""Gravar, ler e mapear arrays em disco; memória compartilhada entre processos."""
import os
import tempfile
import time
from multiprocessing import Pool, shared_memory
from pathlib import Path

import numpy as np


def timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, (time.perf_counter() - start) * 1e3


def disk_demo(work: Path, data: np.ndarray) -> None:
    # 1. .npy: formato binário com cabeçalho (dtype e shape) e leitura exata
    _, t_save = timed(lambda: np.save(work / "a.npy", data))
    loaded, t_load = timed(lambda: np.load(work / "a.npy"))
    print(f"np.save {t_save:6.1f} ms | np.load {t_load:6.1f} ms | idêntico? {np.array_equal(data, loaded)}"
          f" | arquivo {os.path.getsize(work / 'a.npy') / 1e6:.1f} MB")

    # 2. texto (CSV) é muito maior e mais lento (e só é exato porque savetxt usa 18 casas)
    _, t_txt = timed(lambda: np.savetxt(work / "a.csv", data, delimiter=","))
    back, t_back = timed(lambda: np.loadtxt(work / "a.csv", delimiter=","))
    print(f"savetxt {t_txt:7.1f} ms | loadtxt {t_back:7.1f} ms | arquivo {os.path.getsize(work / 'a.csv') / 1e6:.1f} MB"
          f" | idêntico? {np.array_equal(data, back)}")

    # 3. .npz: vários arrays, opcionalmente comprimidos
    np.savez_compressed(work / "multi.npz", points=data[:100], ids=np.arange(100))
    with np.load(work / "multi.npz") as bundle:
        print("\n.npz contém:", bundle.files, "| points:", bundle["points"].shape)

    # 4. np.load recusa objetos por padrão (allow_pickle=False): o risco do pickle, Capítulo 8 do Volume 3
    objs = np.array([{"a": 1}, None], dtype=object)
    np.save(work / "obj.npy", objs, allow_pickle=True)
    try:
        np.load(work / "obj.npy")
    except ValueError as error:
        print("array de objetos sem allow_pickle ->", str(error)[:60], "...")

    # 5. memmap: o array vive no DISCO e o sistema operacional traz as páginas sob demanda
    np.save(work / "big.npy", np.arange(20_000_000, dtype=np.int64))           # 160 MB
    mm = np.load(work / "big.npy", mmap_mode="r")
    print(f"\nmemmap de {mm.nbytes / 1e6:.0f} MB aberto sem ler tudo | tipo: {type(mm).__name__}")
    _, t_slice = timed(lambda: int(mm[10_000_000:10_000_010].sum()))
    print(f"ler 10 elementos do meio: {t_slice:.3f} ms | mm[-1] = {mm[-1]}")
    _, t_full = timed(lambda: int(np.load(work / "big.npy").sum()))
    print(f"carregar tudo e somar: {t_full:6.1f} ms (o memmap só paga pelo que toca)")

    # 6. escrever em memmap: modo w+ cria e grava de volta
    out = np.lib.format.open_memmap(work / "out.npy", mode="w+", dtype=np.float32, shape=(1000, 100))
    out[:] = 1.5
    out.flush()
    print("open_memmap w+ gravado e relido:", np.load(work / "out.npy").mean())


# 7. memória compartilhada entre PROCESSOS: sem copiar nem serializar o array (promessa do Capítulo 16 do Volume 3)
def col_sum(args):
    name, shape, dtype, start, stop = args
    shm = shared_memory.SharedMemory(name=name)
    try:
        arr = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
        return float(arr[:, start:stop].sum())
    finally:
        shm.close()


def shared_demo(data: np.ndarray) -> None:
    shm = shared_memory.SharedMemory(create=True, size=data.nbytes)
    try:
        shared = np.ndarray(data.shape, dtype=data.dtype, buffer=shm.buf)
        shared[:] = data
        step = data.shape[1] // 4
        jobs = [(shm.name, data.shape, data.dtype, i, i + step) for i in range(0, data.shape[1], step)]
        slices = [data[:, i:i + step] for i in range(0, data.shape[1], step)]
        with Pool(4) as pool:
            pool.map(abs, range(4))                                     # aquece: a partida dos processos não entra na conta
            parts, t_shared = timed(lambda: pool.map(col_sum, jobs))
            pickled, t_pickle = timed(lambda: pool.map(np.sum, slices))
        print(f"\n{data.nbytes / 1e6:.0f} MB, 4 processos | SharedMemory: {sum(parts):.4f} em {t_shared:6.1f} ms"
              f" | fatias por pickle: {sum(pickled):.4f} em {t_pickle:6.1f} ms")
        print("somas iguais?", np.isclose(sum(parts), data.sum()))
    finally:
        shm.close()
        shm.unlink()


def main() -> None:
    work = Path(tempfile.mkdtemp(prefix="numpy-cap63-"))
    data = np.random.default_rng(3).random((2000, 1000))                # 16 MB
    print(f"array {data.shape}, {data.nbytes / 1e6:.0f} MB, em {work}\n")
    disk_demo(work, data)
    shared_demo(data)
    big = np.random.default_rng(4).random((8000, 1000))                 # 64 MB
    shared_demo(big)


if __name__ == "__main__":                       # obrigatório com multiprocessing no Windows/macOS (spawn)
    main()
