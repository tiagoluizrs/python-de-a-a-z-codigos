"""Tipos, STRICT, restrições, chaves estrangeiras, RETURNING, UPSERT, adaptadores."""
import datetime as dt
import sqlite3
import warnings

conn = sqlite3.connect(":memory:")

# 1. SQLite tem tipagem por AFINIDADE: aceita praticamente qualquer coisa
conn.execute("CREATE TABLE loose (n INTEGER)")
conn.execute("INSERT INTO loose VALUES ('abc')")
print("tabela comum aceitou texto em INTEGER:", conn.execute("SELECT n, typeof(n) FROM loose").fetchone())

# 2. STRICT: tipos de verdade (3.37+)
conn.execute("CREATE TABLE strict_t (n INTEGER, p REAL, s TEXT) STRICT")
try:
    conn.execute("INSERT INTO strict_t VALUES ('abc', 1.0, 'x')")
except sqlite3.IntegrityError as error:
    print("STRICT recusou:", error)

# 3. chaves estrangeiras estão DESLIGADAS por padrão
conn.execute("CREATE TABLE author (id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE)")
conn.execute("CREATE TABLE book (id INTEGER PRIMARY KEY, title TEXT NOT NULL, author_id INTEGER NOT NULL REFERENCES author(id) ON DELETE CASCADE)")
conn.execute("INSERT INTO book (title, author_id) VALUES ('órfão', 999)")
print("FK desligada: livro com autor inexistente inserido; foreign_keys =", conn.execute("PRAGMA foreign_keys").fetchone()[0])
conn.execute("DELETE FROM book")
conn.commit()                                       # PRAGMA foreign_keys é IGNORADO dentro de uma transação aberta!
conn.execute("PRAGMA foreign_keys = ON")
try:
    conn.execute("INSERT INTO book (title, author_id) VALUES ('órfão', 999)")
except sqlite3.IntegrityError as error:
    print("FK ligada (PRAGMA foreign_keys = ON a CADA conexão):", error)

# 4. UNIQUE, CHECK, NOT NULL levantam IntegrityError
conn.execute("INSERT INTO author (name) VALUES ('Machado')")
for sql in ("INSERT INTO author (name) VALUES ('Machado')", "INSERT INTO author (name) VALUES (NULL)"):
    try:
        conn.execute(sql)
    except sqlite3.IntegrityError as error:
        print("  IntegrityError:", error)

# 5. RETURNING e UPSERT
print("RETURNING:", conn.execute("INSERT INTO author (name) VALUES ('Clarice') RETURNING id, name").fetchone())
conn.execute("CREATE TABLE counter (word TEXT PRIMARY KEY, n INTEGER NOT NULL) STRICT")
for word in "a b a c a b".split():
    conn.execute("INSERT INTO counter VALUES (?, 1) ON CONFLICT(word) DO UPDATE SET n = n + 1", (word,))
print("UPSERT (contagem):", conn.execute("SELECT word, n FROM counter ORDER BY word").fetchall())

# 6. coluna gerada
conn.execute("CREATE TABLE line (price REAL, qty INTEGER, total REAL GENERATED ALWAYS AS (price * qty) STORED) STRICT")
print("coluna gerada:", conn.execute("INSERT INTO line (price, qty) VALUES (2.5, 4) RETURNING total").fetchone())

# 7. datas: o SQLite NÃO tem tipo data; guarde ISO 8601 em TEXT e converta você mesmo
conn.execute("CREATE TABLE event (name TEXT, at TEXT) STRICT")
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter("always")
    conn.execute("INSERT INTO event VALUES (?, ?)", ("x", dt.date.today()))
    print("adaptador padrão de date está obsoleto desde o 3.12:", bool(caught))
conn.execute("INSERT INTO event VALUES (?, ?)", ("lançamento", dt.datetime(2026, 10, 7, 9, 30).isoformat()))
name, at = conn.execute("SELECT name, at FROM event").fetchone()
print("ISO 8601 em TEXT, convertido por você:", name, dt.datetime.fromisoformat(at))
conn.close()
