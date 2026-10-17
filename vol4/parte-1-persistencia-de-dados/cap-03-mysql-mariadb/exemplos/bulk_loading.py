"""Carga em massa: laço, executemany (que o PyMySQL reescreve) e LOAD DATA."""
import os
import tempfile
import time

import mysqlenv

ROWS = [(f"item-{i}", 1.5) for i in range(5_000)]
server = mysqlenv.server_name()
conn = mysqlenv.connect(autocommit=False, local_infile=True)
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS bulk")
cursor.execute("CREATE TABLE bulk (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(40), price DECIMAL(10, 2)) ENGINE=InnoDB")
conn.commit()


def timed(label, func):
    cursor.execute("TRUNCATE TABLE bulk")
    start = time.perf_counter()
    func()
    conn.commit()
    elapsed = time.perf_counter() - start
    cursor.execute("SELECT COUNT(*) AS n FROM bulk")
    print(f"  {label:<40} {elapsed * 1e3:8.1f} ms  ({cursor.fetchone()['n']:,} linhas)")
    return elapsed


print(f"[{server}] inserir {len(ROWS):,} linhas em uma transação:")


def loop():
    for row in ROWS:
        cursor.execute("INSERT INTO bulk (name, price) VALUES (%s, %s)", row)


def many():
    cursor.executemany("INSERT INTO bulk (name, price) VALUES (%s, %s)", ROWS)    # vira INSERT ... VALUES (...), (...), ...


path = os.path.join(tempfile.mkdtemp(), "bulk.csv")
with open(path, "w", encoding="utf-8", newline="\n") as handle:
    for name, price in ROWS:
        handle.write(f"{name},{price}\n")


def load_data():
    cursor.execute(f"LOAD DATA LOCAL INFILE '{path.replace(os.sep, '/')}' INTO TABLE bulk FIELDS TERMINATED BY ',' (name, price)")


slow = timed("laço de execute() (uma ida e volta/linha)", loop)
fast = timed("executemany() (INSERT de várias linhas)", many)
print(f"  executemany foi {slow / fast:,.0f}x mais rápido que o laço")
try:
    timed("LOAD DATA LOCAL INFILE", load_data)
except Exception as error:
    print("  LOAD DATA LOCAL INFILE indisponível:", type(error).__name__, error.args[:2], "(o servidor precisa de local_infile=ON: e isso é um risco de segurança, deixe desligado em produção)")
cursor.execute("DROP TABLE bulk")
conn.commit()
conn.close()
