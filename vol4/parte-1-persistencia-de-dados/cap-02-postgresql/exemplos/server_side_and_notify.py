"""Cursores de servidor (memória constante) e LISTEN/NOTIFY."""
import threading
import time
import tracemalloc

import psycopg

from pgenv import DSN

with psycopg.connect(DSN) as conn:
    N = 1_000_000
    for label, named in (("fetchall() (cursor comum)", False), ("cursor de servidor (named) + fetchmany", True)):
        tracemalloc.start()
        start = time.perf_counter()
        total = 0
        if named:
            with conn.cursor(name="stream") as cursor:
                cursor.itersize = 10_000
                cursor.execute("SELECT g, md5(g::text) FROM generate_series(1, %s) g", (N,))
                while batch := cursor.fetchmany(10_000):
                    total += len(batch)
        else:
            rows = conn.execute("SELECT g, md5(g::text) FROM generate_series(1, %s) g", (N,)).fetchall()
            total = len(rows)
            del rows
        peak = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()
        conn.rollback()
        print(f"  {label:<40} {total:,} linhas | pico de memória {peak / 1e6:7.1f} MB | {time.perf_counter() - start:.2f} s")

# LISTEN / NOTIFY: o banco avisa a aplicação
listener = psycopg.connect(DSN, autocommit=True)
listener.execute("LISTEN pedidos")


def notify_later():
    time.sleep(0.2)
    with psycopg.connect(DSN, autocommit=True) as other:
        other.execute("SELECT pg_notify('pedidos', %s)", ("pedido 42 criado",))


threading.Thread(target=notify_later).start()
start = time.perf_counter()
for notice in listener.notifies(timeout=3, stop_after=1):
    print(f"LISTEN/NOTIFY: canal={notice.channel!r} payload={notice.payload!r} após {time.perf_counter() - start:.2f} s, sem consultar em laço")
listener.close()
