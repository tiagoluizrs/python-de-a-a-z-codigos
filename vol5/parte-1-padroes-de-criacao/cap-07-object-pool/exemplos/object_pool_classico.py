"""Object Pool, forma clássica: reaproveitar objetos CAROS de criar, entregando-os por empréstimo (acquire/release)."""
import queue
import sqlite3
import tempfile
import time
from pathlib import Path


# --- 1. o problema: abrir um recurso caro a cada uso ---
folder = tempfile.mkdtemp()
db_file = str(Path(folder) / "loja.db")
setup = sqlite3.connect(db_file)
setup.execute("create table items (id integer primary key, name text)")
setup.executemany("insert into items (name) values (?)", [(f"item {i}",) for i in range(100)])
setup.commit()
setup.close()


def query_with_new_connection():
    conn = sqlite3.connect(db_file)                          # abrir arquivo, ler cabeçalho, preparar o estado
    try:
        return conn.execute("select count(*) from items").fetchone()[0]
    finally:
        conn.close()


def best(fn, n=2000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


print(f"abrir e fechar uma conexão a cada consulta: {best(query_with_new_connection):6.1f} µs por consulta")


# --- 2. a forma clássica: um pool com acquire e release ---
class PoolExhausted(TimeoutError):
    pass


class ConnectionPool:
    def __init__(self, factory, size):
        self._factory, self._size = factory, size
        self._idle = queue.Queue()
        self._created = 0
        self._leased = set()

    def acquire(self, timeout=1.0):
        try:
            conn = self._idle.get_nowait()                    # reaproveitar uma ociosa
        except queue.Empty:
            if self._created < self._size:                    # ou criar, até o limite
                self._created += 1
                conn = self._factory()
            else:
                try:
                    conn = self._idle.get(timeout=timeout)    # ou esperar alguém devolver
                except queue.Empty:
                    raise PoolExhausted(f"nenhuma conexão livre em {timeout}s (limite {self._size})") from None
        self._leased.add(id(conn))
        return conn

    def release(self, conn):
        if id(conn) not in self._leased:
            raise ValueError("objeto não emprestado por este pool (ou já devolvido)")
        self._leased.discard(id(conn))
        self._idle.put(conn)

    def close(self):
        while not self._idle.empty():
            self._idle.get_nowait().close()


pool = ConnectionPool(lambda: sqlite3.connect(db_file, check_same_thread=False), size=2)


def query_with_pool():
    conn = pool.acquire()
    try:
        return conn.execute("select count(*) from items").fetchone()[0]
    finally:
        pool.release(conn)                                    # SEMPRE devolver, mesmo com erro: o try/finally é obrigatório


print(f"reaproveitando conexões de um pool:          {best(query_with_pool):6.1f} µs por consulta")
print("resultado igual:", query_with_new_connection(), query_with_pool(), "| conexões criadas pelo pool:", pool._created)

# --- 3. a primeira armadilha: esquecer de devolver (vazamento) esgota o pool ---
a = pool.acquire()
b = pool.acquire()                                            # as duas conexões do pool estão emprestadas
t0 = time.perf_counter()
try:
    pool.acquire(timeout=0.2)
except PoolExhausted as error:
    print(f"\npool esgotado após {time.perf_counter() - t0:.1f}s de espera:", error)
pool.release(a)
pool.release(b)
try:
    pool.release(b)
except ValueError as error:
    print("devolver duas vezes é detectado:", error)

# --- 4. a segunda armadilha: o objeto devolvido volta com ESTADO da vida anterior ---
single = ConnectionPool(lambda: sqlite3.connect(db_file, check_same_thread=False), size=1)
conn = single.acquire()
conn.execute("create temp table rascunho (x integer)")        # algo que o próximo usuário não deveria enxergar
single.release(conn)
conn2 = single.acquire()
print("\no próximo empréstimo enxerga o rascunho do anterior:", conn2.execute("select name from sqlite_temp_master").fetchall(), "(o pool precisa de um reset ao devolver)")
single.release(conn2)
single.close()
pool.close()

# --- 5. o custo de criar um objeto barato: o pool piora ---
class Point:
    def __init__(self):
        self.x = self.y = 0


point_pool = queue.Queue()
for _ in range(4):
    point_pool.put(Point())


def with_new_point():
    p = Point()
    p.x = 1


def with_pooled_point():
    p = point_pool.get_nowait()
    p.x = 1
    point_pool.put(p)


print(f"\nobjeto barato: criar {best(with_new_point, 200_000) * 1000:5.0f} ns | pegar e devolver de um pool {best(with_pooled_point, 200_000) * 1000:5.0f} ns")
print("pool só se paga quando CRIAR é muito mais caro que emprestar (microssegundos ou mais, contra centenas de nanossegundos de um Queue)")
