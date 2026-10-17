"""Transações: os três modos de controle, rollback, savepoints, o with."""
import contextlib
import sqlite3


def balance(conn, name):
    return conn.execute("SELECT balance FROM account WHERE name = ?", (name,)).fetchone()[0]


def setup(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS account (name TEXT PRIMARY KEY, balance INTEGER NOT NULL CHECK (balance >= 0))")
    conn.execute("DELETE FROM account")
    conn.executemany("INSERT INTO account VALUES (?, ?)", [("ana", 100), ("bia", 50)])
    conn.commit()


def transfer(conn, source, target, amount):
    with conn:                                      # commit se sair bem, ROLLBACK se levantar (e NÃO fecha a conexão)
        conn.execute("UPDATE account SET balance = balance - ? WHERE name = ?", (amount, source))
        conn.execute("UPDATE account SET balance = balance + ? WHERE name = ?", (amount, target))


conn = sqlite3.connect(":memory:")
print("autocommit padrão (legacy) =", conn.autocommit, "(-1: o módulo abre transações sozinho antes de INSERT/UPDATE/DELETE)")
setup(conn)

transfer(conn, "ana", "bia", 30)
print("depois de transfer(30):", balance(conn, "ana"), balance(conn, "bia"))
try:
    transfer(conn, "ana", "bia", 500)               # o CHECK falha no primeiro UPDATE
except sqlite3.IntegrityError as error:
    print("falhou:", error, "| nada mudou:", balance(conn, "ana"), balance(conn, "bia"))

# falha NO MEIO: o primeiro UPDATE valeu, o segundo não existe -> o rollback desfaz os dois
try:
    with conn:
        conn.execute("UPDATE account SET balance = balance - 10 WHERE name = 'ana'")
        raise RuntimeError("queda de energia simulada")
except RuntimeError:
    print("após erro no meio: ana =", balance(conn, "ana"), "(os 10 voltaram)")

# SAVEPOINT: transação dentro da transação
conn.isolation_level = None                         # controle manual: nós emitimos BEGIN/COMMIT
conn.execute("BEGIN")
conn.execute("UPDATE account SET balance = balance + 1 WHERE name = 'ana'")
conn.execute("SAVEPOINT parte2")
conn.execute("UPDATE account SET balance = balance + 1000 WHERE name = 'ana'")
conn.execute("ROLLBACK TO parte2")                  # desfaz só o que veio depois do savepoint
conn.execute("COMMIT")
print("depois do savepoint: ana =", balance(conn, "ana"))

# O modo moderno (3.12+): autocommit=False -> há SEMPRE uma transação aberta
modern = sqlite3.connect(":memory:", autocommit=False)
modern.execute("CREATE TABLE t (x)")
modern.execute("INSERT INTO t VALUES (1)")
modern.rollback()
try:
    modern.execute("SELECT 1 FROM t")
    print("autocommit=False: o rollback desfez só o INSERT; a tabela continua")
except sqlite3.OperationalError:
    print("autocommit=False: o rollback desfez até o CREATE TABLE (DDL também é transacional no SQLite)")

# fechar de verdade: o with da conexão NÃO fecha
with contextlib.closing(sqlite3.connect(":memory:")) as c:
    c.execute("SELECT 1")
print("closing() fecha a conexão ao sair do bloco")
