"""Conexões custam; uma conexão NÃO é compartilhável entre threads; pools."""
import queue
import threading
import time

import mysql.connector.pooling

import mysqlenv

host, port = mysqlenv.SERVERS[mysqlenv.server_name()]
KW = dict(host=host, port=port, user="root", password="root", database="livro")

start = time.perf_counter()
for _ in range(20):
    mysqlenv.connect().close()
cost = (time.perf_counter() - start) / 20
print(f"abrir e fechar uma conexão PyMySQL: {cost * 1e3:.1f} ms")

# 1. o pool do mysql-connector
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="livro", pool_size=4, **KW)
start = time.perf_counter()
for _ in range(500):
    conn = pool.get_connection()
    conn.close()                                       # close() DEVOLVE ao pool
checkout = (time.perf_counter() - start) / 500
print(f"emprestar do pool do mysql-connector: {checkout * 1e6:.0f} us ({cost / checkout:,.0f}x mais barato)")
held = [pool.get_connection() for _ in range(4)]
try:
    pool.get_connection()
except mysql.connector.errors.PoolError as error:
    print("pool de 4 esgotado ->", type(error).__name__, "-", error)
for conn in held:
    conn.close()


# 2. o PyMySQL não traz pool: um pool mínimo com queue.Queue (Capítulo 15 do Volume 3) cobre o essencial
class MiniPool:
    def __init__(self, size):
        self._idle = queue.Queue()
        for _ in range(size):
            self._idle.put(mysqlenv.connect(autocommit=True))

    def run(self, sql):
        conn = self._idle.get(timeout=5)
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
        finally:
            self._idle.put(conn)

    def close(self):
        while not self._idle.empty():
            self._idle.get().close()


mini = MiniPool(4)
start = time.perf_counter()
threads = [threading.Thread(target=mini.run, args=("SELECT SLEEP(0.2)",)) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"8 consultas de 0,2 s em um MiniPool de 4 conexões, 8 threads: {time.perf_counter() - start:.2f} s (2 rodadas)")
mini.close()

# 3. compartilhar UMA conexão entre threads: protocolo embaralhado
conn = mysqlenv.connect(autocommit=True)
errors = []


def abuse():
    try:
        for _ in range(30):
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 AS x")
                cursor.fetchall()
    except Exception as error:
        errors.append(type(error).__name__)


threads = [threading.Thread(target=abuse) for _ in range(8)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("3. 8 threads usando UMA conexão PyMySQL:", f"{len(errors)} threads falharam" + (f" ({sorted(set(errors))})" if errors else " (nenhuma desta vez: sorte; não é garantido)"))
conn.close()
