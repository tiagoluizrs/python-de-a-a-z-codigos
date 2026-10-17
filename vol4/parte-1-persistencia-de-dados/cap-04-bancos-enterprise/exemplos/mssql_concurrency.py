"""SQL Server: leitores bloqueados, READPAST, RCSI e deadlock."""
import threading
import time

import mssql_python

from envs import MSSQL_CS


def connect(autocommit=False, db="livro"):
    return mssql_python.connect(MSSQL_CS.format(db=db), autocommit=autocommit)


master = connect(autocommit=True, db="master")
master.cursor().execute("ALTER DATABASE livro SET READ_COMMITTED_SNAPSHOT OFF WITH ROLLBACK IMMEDIATE")   # ponto de partida conhecido
admin = connect(autocommit=True)
cursor = admin.cursor()
cursor.execute("IF OBJECT_ID('acc') IS NOT NULL DROP TABLE acc")
cursor.execute("CREATE TABLE acc (id INT PRIMARY KEY, bal INT)")
cursor.execute("INSERT INTO acc VALUES (1, 100), (2, 100)")
cursor.execute("SELECT is_read_committed_snapshot_on FROM sys.databases WHERE name = 'livro'")
print("RCSI ligado?", bool(cursor.fetchone()[0]), "(padrão: DESLIGADO: leitores esperam escritores)")

# 1. READ COMMITTED com travas: um escritor BLOQUEIA os leitores
writer = connect()
writer.cursor().execute("UPDATE acc SET bal = 1 WHERE id = 1")           # transação aberta, linha travada
reader = connect(autocommit=True)
rcur = reader.cursor()
rcur.execute("SET LOCK_TIMEOUT 500")
start = time.perf_counter()
try:
    rcur.execute("SELECT bal FROM acc WHERE id = 1")
    print("leitor passou:", rcur.fetchone())
except Exception as error:
    print(f"1. leitor BLOQUEADO pelo escritor e desistiu em {time.perf_counter() - start:.1f} s: {type(error).__name__} (timeout de trava)")
rcur.execute("SELECT bal FROM acc WITH (READPAST) WHERE id = 1")
print("   WITH (READPAST) pula a linha travada:", rcur.fetchall(), "| (NOLOCK lê dado SUJO: evite)")
writer.rollback()
writer.close()
reader.close()

# 2. RCSI: leitores usam versões, como o PostgreSQL
master.cursor().execute("ALTER DATABASE livro SET READ_COMMITTED_SNAPSHOT ON WITH ROLLBACK IMMEDIATE")   # derruba as conexões abertas!
admin.close()
admin = connect(autocommit=True)
writer = connect()
writer.cursor().execute("UPDATE acc SET bal = 1 WHERE id = 1")
reader = connect(autocommit=True)
rcur = reader.cursor()
start = time.perf_counter()
rcur.execute("SELECT bal FROM acc WHERE id = 1")
print(f"2. com RCSI o leitor viu {rcur.fetchone()[0]} (valor confirmado) em {(time.perf_counter() - start) * 1e3:.0f} ms, sem esperar")
writer.rollback()
writer.close()
reader.close()
master.cursor().execute("ALTER DATABASE livro SET READ_COMMITTED_SNAPSHOT OFF WITH ROLLBACK IMMEDIATE")
admin.close()
admin = connect(autocommit=True)


# 3. deadlock: o SQL Server derruba UMA transação (erro 1205)
def transfer(first, second, name, results, ordered):
    conn = connect()
    cur = conn.cursor()
    try:
        if ordered:
            cur.execute("SELECT id FROM acc WITH (UPDLOCK) WHERE id IN (?, ?) ORDER BY id", (first, second))
            cur.fetchall()
        cur.execute("UPDATE acc SET bal = bal - 1 WHERE id = ?", (first,))
        time.sleep(0.3)
        cur.execute("UPDATE acc SET bal = bal + 1 WHERE id = ?", (second,))
        conn.commit()
        results[name] = "ok"
    except Exception as error:
        results[name] = "DEADLOCK (1205): a vítima foi derrubada" if "deadlock" in str(error).lower() else f"{type(error).__name__}"
        conn.rollback()
    finally:
        conn.close()


for label, ordered in (("3. ordens opostas", False), ("   travando em ordem", True)):
    results = {}
    threads = [threading.Thread(target=transfer, args=(1, 2, "T1", results, ordered)), threading.Thread(target=transfer, args=(2, 1, "T2", results, ordered))]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"{label}: {dict(sorted(results.items()))}")
admin.cursor().execute("DROP TABLE acc")
admin.close()
master.close()
