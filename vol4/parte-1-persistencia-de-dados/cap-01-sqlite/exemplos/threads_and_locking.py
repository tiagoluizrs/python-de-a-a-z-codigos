"""SQLite e concorrência: uma conexão por thread, WAL, busy_timeout e 'database is locked'."""
import os
import sqlite3
import tempfile
import threading
import time

# 1. uma conexão NÃO pode ser usada por outra thread (por padrão)
conn = sqlite3.connect(":memory:")


def other_thread():
    try:
        conn.execute("SELECT 1")
    except sqlite3.ProgrammingError as error:
        print("outra thread usando a conexão:", type(error).__name__, "-", str(error)[:60], "...")


t = threading.Thread(target=other_thread)
t.start()
t.join()
print("sqlite3.threadsafety =", sqlite3.threadsafety, "(3 = a biblioteca é segura; a REGRA do Python continua sendo: uma conexão por thread)")

path = os.path.join(tempfile.mkdtemp(), "shared.db")
setup = sqlite3.connect(path)
setup.execute("PRAGMA journal_mode = WAL")
setup.execute("CREATE TABLE log (id INTEGER PRIMARY KEY, who TEXT)")
setup.commit()
setup.close()

# 2. escritores simultâneos: só UM por vez; os outros ESPERAM (busy_timeout) ou falham
def writer(name, timeout, hold, results):
    c = sqlite3.connect(path, timeout=timeout)
    try:
        c.execute("BEGIN IMMEDIATE")                # pede a trava de escrita já no início
        time.sleep(hold)
        c.execute("INSERT INTO log (who) VALUES (?)", (name,))
        c.commit()
        results[name] = "ok"
    except sqlite3.OperationalError as error:
        results[name] = f"FALHOU: {error}"
    finally:
        c.close()


for timeout in (0.05, 5.0):
    results = {}
    threads = [threading.Thread(target=writer, args=(f"w{i}", timeout, 0.3, results)) for i in range(3)]
    start = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"3 escritores (cada um segura a trava 0,3 s), timeout={timeout}: {sorted(results.values())} em {time.perf_counter() - start:.2f} s")

# 3. WAL: leitores NÃO bloqueiam o escritor (nem o contrário)
reader = sqlite3.connect(path)
reader.execute("BEGIN")
before = reader.execute("SELECT COUNT(*) FROM log").fetchone()[0]
w = sqlite3.connect(path)
w.execute("INSERT INTO log (who) VALUES ('durante a leitura')")
w.commit()
print("WAL: escrita concluída enquanto havia uma leitura aberta; o leitor ainda vê", reader.execute("SELECT COUNT(*) FROM log").fetchone()[0], "(antes:", before, ") — isolamento por snapshot")
reader.rollback()
print("depois de encerrar a transação, o leitor vê", reader.execute("SELECT COUNT(*) FROM log").fetchone()[0])
