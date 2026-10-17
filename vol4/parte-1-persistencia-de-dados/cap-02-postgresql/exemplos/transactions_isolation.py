"""Transações, savepoints e níveis de isolamento (MVCC)."""
import psycopg
from psycopg.rows import dict_row

from pgenv import DSN

with psycopg.connect(DSN, autocommit=True) as admin:
    admin.execute("DROP TABLE IF EXISTS acc")
    admin.execute("CREATE TABLE acc (id int PRIMARY KEY, bal int NOT NULL CHECK (bal >= 0))")
    admin.execute("INSERT INTO acc VALUES (1, 100), (2, 50)")

# 1. conn.transaction(): o jeito explícito (com SAVEPOINT quando aninhado)
with psycopg.connect(DSN, row_factory=dict_row, autocommit=True) as conn:
    with conn.transaction():
        conn.execute("UPDATE acc SET bal = bal - 30 WHERE id = 1")
        try:
            with conn.transaction():                          # aninhado = SAVEPOINT
                conn.execute("UPDATE acc SET bal = bal - 1000 WHERE id = 1")   # viola o CHECK
        except psycopg.errors.CheckViolation:
            print("o savepoint interno foi desfeito; a transação externa segue")
        conn.execute("UPDATE acc SET bal = bal + 30 WHERE id = 2")
    print("saldos:", [r["bal"] for r in conn.execute("SELECT bal FROM acc ORDER BY id")])

# 2. READ COMMITTED (padrão): cada comando vê o que foi confirmado ATÉ ALI
a = psycopg.connect(DSN, autocommit=False)
b = psycopg.connect(DSN, autocommit=True)
print("\nnível padrão:", a.execute("SHOW transaction_isolation").fetchone()[0])
print("A lê  :", a.execute("SELECT bal FROM acc WHERE id = 1").fetchone()[0])
b.execute("UPDATE acc SET bal = 999 WHERE id = 1")
print("A lê de novo (B confirmou no meio):", a.execute("SELECT bal FROM acc WHERE id = 1").fetchone()[0], "<- leitura NÃO repetível")
a.rollback()

# 3. REPEATABLE READ: um snapshot para a transação inteira
a.isolation_level = psycopg.IsolationLevel.REPEATABLE_READ
b.execute("UPDATE acc SET bal = 100 WHERE id = 1")
print("REPEATABLE READ, A lê  :", a.execute("SELECT bal FROM acc WHERE id = 1").fetchone()[0])
b.execute("UPDATE acc SET bal = 777 WHERE id = 1")
print("REPEATABLE READ, A lê de novo:", a.execute("SELECT bal FROM acc WHERE id = 1").fetchone()[0], "<- o mesmo (snapshot)")
try:
    a.execute("UPDATE acc SET bal = bal + 1 WHERE id = 1")
except psycopg.errors.SerializationFailure as error:
    print("e atualizar a linha que mudou: SerializationFailure", error.sqlstate, "-> RETENTE a transação inteira")
a.rollback()

# 4. SELECT ... FOR UPDATE: bloquear a linha enquanto você decide
a.isolation_level = None
with a.transaction():
    a.execute("SELECT bal FROM acc WHERE id = 1 FOR UPDATE")
    try:
        b2 = psycopg.connect(DSN, autocommit=True)
        b2.execute("SET lock_timeout = '200ms'")
        b2.execute("UPDATE acc SET bal = 1 WHERE id = 1")
    except psycopg.errors.LockNotAvailable as error:
        print("\nFOR UPDATE: outra conexão esperou e desistiu pelo lock_timeout:", error.sqlstate)
a.close()
b.close()
