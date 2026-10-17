"""Object Pool em Python: um queue.Queue e um gerenciador de contexto; e os pools que a biblioteca padrão já traz."""
import contextlib
import io
import queue
import sqlite3
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

folder = tempfile.mkdtemp()
db_file = str(Path(folder) / "loja.db")
setup = sqlite3.connect(db_file)
setup.execute("create table items (id integer primary key, name text)")
setup.executemany("insert into items (name) values (?)", [(f"item {i}",) for i in range(100)])
setup.commit()
setup.close()


def best(fn, n=2000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


# --- 1. o pool em 12 linhas: uma fila de objetos ociosos + um gerenciador de contexto ---
class Pool:
    def __init__(self, factory, size, reset=None):
        self._idle = queue.Queue(maxsize=size)
        for _ in range(size):                                  # criação antecipada: simples, e o limite é a própria fila
            self._idle.put(factory())
        self._reset = reset or (lambda obj: None)

    @contextlib.contextmanager
    def lease(self, timeout=None):
        obj = self._idle.get(timeout=timeout)                  # bloqueia até haver um livre (queue.Empty se estourar o timeout)
        try:
            yield obj
        finally:
            self._reset(obj)                                   # limpar o estado ANTES de devolver
            self._idle.put(obj)                                # devolver mesmo com exceção: é o que o 'with' garante

    def close(self, closer=lambda obj: obj.close()):
        while not self._idle.empty():
            closer(self._idle.get_nowait())


pool = Pool(lambda: sqlite3.connect(db_file, check_same_thread=False), size=2, reset=lambda c: c.rollback())


def query_with_pool():
    with pool.lease() as conn:                                 # impossível esquecer de devolver
        return conn.execute("select count(*) from items").fetchone()[0]


def query_new():
    conn = sqlite3.connect(db_file)
    try:
        return conn.execute("select count(*) from items").fetchone()[0]
    finally:
        conn.close()


print(f"com o pool (with):               {best(query_with_pool):6.1f} µs por consulta")
print(f"abrindo uma conexão a cada vez:  {best(query_new):6.1f} µs por consulta")

# o `with` devolve mesmo quando o código dentro falha
try:
    with pool.lease() as conn:
        raise RuntimeError("falhou no meio do trabalho")
except RuntimeError:
    pass
print("depois de uma exceção, o objeto voltou ao pool:", pool._idle.qsize(), "livres de 2")

# --- 2. vários threads dividindo poucos objetos: a fila faz a espera (e o limite) ---
active, peak, lock = 0, 0, threading.Lock()


def worker(_):
    global active, peak
    with pool.lease() as conn:
        with lock:
            active += 1
            peak = max(peak, active)
        time.sleep(0.01)                                       # trabalho que segura o objeto
        with lock:
            active -= 1


with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(worker, range(16)))
print(f"\n8 threads e 16 tarefas, pool de 2: no máximo {peak} objetos emprestados ao mesmo tempo (o resto esperou na fila)")
pool.close()

# --- 3. outro pool: reaproveitar BUFFERS em vez de alocar um novo a cada leitura ---
data = io.BytesIO(bytes(range(256)) * 4096)                    # 1 MiB


def read_alloc():
    data.seek(0)
    total = 0
    while chunk := data.read(65536):                           # cada read() aloca um bytes novo de até 64 KiB
        total += len(chunk)
    return total


buffer = bytearray(65536)


def read_reuse():
    data.seek(0)
    total = 0
    while n := data.readinto(buffer):                          # o MESMO bytearray é reaproveitado
        total += n
    return total


print(f"\nler 1 MiB alocando um chunk novo a cada leitura: {best(read_alloc, 3000):6.1f} µs")
print(f"ler 1 MiB reaproveitando um bytearray (readinto): {best(read_reuse, 3000):6.1f} µs")

# --- 4. a biblioteca padrão já tem pools: ThreadPoolExecutor reaproveita THREADS ---
def task():
    return 1


def spawn_thread():
    t = threading.Thread(target=task)
    t.start()
    t.join()


executor = ThreadPoolExecutor(max_workers=4)


def use_executor():
    executor.submit(task).result()


print(f"\ncriar e juntar uma thread a cada tarefa: {best(spawn_thread, 1000):6.1f} µs")
print(f"enviar a tarefa a um ThreadPoolExecutor: {best(use_executor, 1000):6.1f} µs")
executor.shutdown()

# --- 5. alternativa sem pool nenhum: um recurso por thread ---
local = threading.local()


def thread_connection():
    if not hasattr(local, "conn"):
        local.conn = sqlite3.connect(db_file)
    return local.conn


def query_thread_local():
    return thread_connection().execute("select count(*) from items").fetchone()[0]


print(f"\num recurso por thread (threading.local): {best(query_thread_local):6.1f} µs por consulta (sem fila, sem limite, uma conexão por thread viva)")
print("quando o objeto não precisa ser dividido entre threads, threading.local dispensa o pool")
