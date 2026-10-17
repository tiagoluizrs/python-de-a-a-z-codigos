"""A MESMA tarefa em cinco dialetos: o que muda e o que não muda."""
import sqlite3

DIALECTS = {
    #           paginação                                     upsert                                      chave gerada            aspas
    "sqlite":     ("LIMIT :n OFFSET :o",                       "ON CONFLICT (id) DO UPDATE SET",             "RETURNING id",          '"x"'),
    "postgresql": ("LIMIT n OFFSET o",                         "ON CONFLICT (id) DO UPDATE SET",             "RETURNING id",          '"x"'),
    "mysql":      ("LIMIT n OFFSET o",                         "ON DUPLICATE KEY UPDATE",                    "cursor.lastrowid",      "`x`"),
    "mariadb":    ("LIMIT n OFFSET o",                         "ON DUPLICATE KEY UPDATE",                    "RETURNING id",          "`x`"),
    "oracle":     ("OFFSET o ROWS FETCH NEXT n ROWS ONLY",     "MERGE INTO ... USING dual ...",              "RETURNING id INTO :v",  '"X" (maiúsculas)'),
    "mssql":      ("OFFSET o ROWS FETCH NEXT n ROWS ONLY",     "MERGE ... USING (SELECT ...) ...;",          "OUTPUT INSERTED.id",    "[x]"),
}

print(f"{'dialeto':<12}{'paginação':<40}{'upsert':<34}{'chave gerada':<24}aspas")
for name, (page, upsert, key, quote) in DIALECTS.items():
    print(f"{name:<12}{page:<40}{upsert:<34}{key:<24}{quote}")

print()
print("O que NÃO muda: SELECT/JOIN/GROUP BY/janelas, transações, índices, parâmetros (só o SÍMBOLO muda:")
print("  sqlite/mssql-python: ?   |   psycopg/PyMySQL: %s   |   oracledb: :1 ou :nome)")

# o que a camada Python deve esconder: uma função por diferença
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE item (id INTEGER PRIMARY KEY, name TEXT)")
conn.executemany("INSERT INTO item (name) VALUES (?)", [(f"n{i}",) for i in range(20)])
print("sqlite, página 3 de 5:", conn.execute("SELECT name FROM item ORDER BY id LIMIT ? OFFSET ?", (5, 10)).fetchall())
