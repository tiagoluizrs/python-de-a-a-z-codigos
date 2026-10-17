"""InnoDB: REPEATABLE READ, travas, deadlock (1213), timeout de trava (1205), SKIP LOCKED."""
import threading
import time

import pymysql

import mysqlenv

server = mysqlenv.server_name()
print(f"=== {server} ===")
admin = mysqlenv.connect(autocommit=True)
cur = admin.cursor()
cur.execute("DROP TABLE IF EXISTS acc")
cur.execute("CREATE TABLE acc (id INT PRIMARY KEY, bal INT NOT NULL) ENGINE=InnoDB")
cur.execute("INSERT INTO acc VALUES (1, 100), (2, 100)")

# 1. REPEATABLE READ é o PADRÃO do MySQL/MariaDB (no PostgreSQL é READ COMMITTED)
a = mysqlenv.connect(autocommit=False)
b = mysqlenv.connect(autocommit=True)
ca, cb = a.cursor(), b.cursor()
ca.execute("SELECT @@transaction_isolation AS level")
print("1. nível padrão:", ca.fetchone()["level"])
ca.execute("SELECT bal FROM acc WHERE id = 1")
print("   A lê:", ca.fetchone()["bal"])
cb.execute("UPDATE acc SET bal = 555 WHERE id = 1")
ca.execute("SELECT bal FROM acc WHERE id = 1")
print("   B confirmou 555; A lê de novo:", ca.fetchone()["bal"], "(o snapshot da transação de A)")
try:
    ca.execute("SELECT bal FROM acc WHERE id = 1 FOR UPDATE")
    print("   mas SELECT ... FOR UPDATE lê o dado ATUAL:", ca.fetchone()["bal"], "(leitura 'de travamento' ignora o snapshot)")
except pymysql.err.OperationalError as error:
    print("   SELECT ... FOR UPDATE neste servidor RECUSA ler a linha que mudou depois do snapshot: erro", error.args[0],
          "(innodb_snapshot_isolation, ligado por padrão no MariaDB 11.6+): REPITA a transação")
a.rollback()


# 2. deadlock: o InnoDB derruba uma das transações (erro 1213)
def transfer(first, second, name, results, ordered=False):
    conn = mysqlenv.connect(autocommit=False)
    c = conn.cursor()
    try:
        if ordered:
            c.execute("SELECT id FROM acc WHERE id IN (%s, %s) ORDER BY id FOR UPDATE", (first, second))
        else:
            c.execute("UPDATE acc SET bal = bal - 1 WHERE id = %s", (first,))
        time.sleep(0.3)
        c.execute("UPDATE acc SET bal = bal - 1 WHERE id = %s", (first,)) if ordered else None
        c.execute("UPDATE acc SET bal = bal + 1 WHERE id = %s", (second,))
        conn.commit()
        results[name] = "ok"
    except pymysql.err.OperationalError as error:
        conn.rollback()
        results[name] = f"erro {error.args[0]}: {error.args[1][:34]}..."
    finally:
        conn.close()


for label, ordered in (("2. ordens opostas", False), ("   travando em ordem", True)):
    results = {}
    threads = [threading.Thread(target=transfer, args=(1, 2, "T1", results, ordered)), threading.Thread(target=transfer, args=(2, 1, "T2", results, ordered))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"{label}: {dict(sorted(results.items()))}")

# 3. espera por trava: innodb_lock_wait_timeout (50 s por padrão!) -> erro 1205
ca.execute("SELECT * FROM acc WHERE id = 1 FOR UPDATE")          # A segura a linha
cb.execute("SET SESSION innodb_lock_wait_timeout = 1")
start = time.perf_counter()
try:
    cb.execute("UPDATE acc SET bal = 0 WHERE id = 1")
except pymysql.err.OperationalError as error:
    print(f"3. B esperou {time.perf_counter() - start:.1f} s e levou o erro {error.args[0]} (Lock wait timeout exceeded). Padrão do servidor: 50 s!")
a.rollback()

# 4. fila: SKIP LOCKED e NOWAIT (MySQL 8.0+ e MariaDB 10.6+)
ca.execute("SELECT id FROM acc ORDER BY id LIMIT 1 FOR UPDATE")
cb.execute("SELECT id FROM acc ORDER BY id LIMIT 1 FOR UPDATE SKIP LOCKED")
print("4. SKIP LOCKED: A travou a linha", 1, "-> B pulou para a linha", cb.fetchone()["id"])
try:
    cb.execute("SELECT id FROM acc WHERE id = 1 FOR UPDATE NOWAIT")
except pymysql.err.OperationalError as error:
    print("   NOWAIT falha na hora com o erro", error.args[0])
a.rollback()
cur.execute("DROP TABLE acc")
a.close()
b.close()
admin.close()
