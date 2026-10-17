"""Padrões de concorrência no PostgreSQL: fila com SKIP LOCKED, deadlock e a correção."""
import threading
import time

import psycopg

from pgenv import DSN

with psycopg.connect(DSN, autocommit=True) as admin:
    admin.execute("DROP TABLE IF EXISTS job")
    admin.execute("CREATE TABLE job (id serial PRIMARY KEY, state text NOT NULL DEFAULT 'new', owner text)")
    admin.execute("INSERT INTO job (state) SELECT 'new' FROM generate_series(1, 10)")

# 1. Fila de tarefas: vários trabalhadores, nenhum pega a mesma tarefa
claimed = {}


def worker(name):
    with psycopg.connect(DSN) as conn:                         # a transação só termina ao sair do with
        rows = conn.execute(
            """UPDATE job SET state = 'running', owner = %s
               WHERE id IN (SELECT id FROM job WHERE state = 'new' ORDER BY id LIMIT 5 FOR UPDATE SKIP LOCKED)
               RETURNING id""", (name,)).fetchall()
        time.sleep(0.2)                                        # segura as linhas travadas: o outro PULA, não espera
        claimed[name] = sorted(r[0] for r in rows)


threads = [threading.Thread(target=worker, args=(n,)) for n in ("A", "B")]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("FOR UPDATE SKIP LOCKED:", claimed, "-> disjuntos:", not set(claimed["A"]) & set(claimed["B"]))

# 2. Deadlock: duas transações travam as mesmas linhas em ORDENS OPOSTAS
with psycopg.connect(DSN, autocommit=True) as admin:
    admin.execute("DROP TABLE IF EXISTS acc")
    admin.execute("CREATE TABLE acc (id int PRIMARY KEY, bal int)")
    admin.execute("INSERT INTO acc VALUES (1, 100), (2, 100)")


def transfer(first, second, name, results):
    try:
        with psycopg.connect(DSN) as conn:
            conn.execute("UPDATE acc SET bal = bal - 1 WHERE id = %s", (first,))
            time.sleep(0.3)
            conn.execute("UPDATE acc SET bal = bal + 1 WHERE id = %s", (second,))
        results[name] = "ok"
    except psycopg.errors.DeadlockDetected as error:
        results[name] = f"deadlock ({error.sqlstate}): o PostgreSQL derrubou UMA das transações"


results = {}
threads = [threading.Thread(target=transfer, args=(1, 2, "T1", results)), threading.Thread(target=transfer, args=(2, 1, "T2", results))]
start = time.perf_counter()
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"ordens opostas ({time.perf_counter() - start:.1f} s):", results)


# 3. A correção: travar SEMPRE na mesma ordem (o Capítulo 15 do Volume 3 em versão SQL)
def ordered_transfer(source, target, name, results):
    with psycopg.connect(DSN) as conn:
        conn.execute("SELECT id FROM acc WHERE id IN (%s, %s) ORDER BY id FOR UPDATE", (source, target))
        time.sleep(0.3)
        conn.execute("UPDATE acc SET bal = bal - 1 WHERE id = %s", (source,))
        conn.execute("UPDATE acc SET bal = bal + 1 WHERE id = %s", (target,))
    results[name] = "ok"


results = {}
threads = [threading.Thread(target=ordered_transfer, args=(1, 2, "T1", results)), threading.Thread(target=ordered_transfer, args=(2, 1, "T2", results))]
start = time.perf_counter()
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"travando em ordem ({time.perf_counter() - start:.1f} s):", results, "(uma espera a outra, sem deadlock)")

# 4. Prazos: statement_timeout e lock_timeout
with psycopg.connect(DSN, autocommit=True) as conn:
    conn.execute("SET statement_timeout = '100ms'")
    try:
        conn.execute("SELECT pg_sleep(1)")
    except psycopg.errors.QueryCanceled as error:
        print("statement_timeout derrubou a consulta lenta:", error.sqlstate)
    conn.execute("DROP TABLE job, acc")
