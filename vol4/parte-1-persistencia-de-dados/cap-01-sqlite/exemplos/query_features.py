"""Recursos poderosos: janelas, CTE recursiva, JSON, FTS5, funções em Python."""
import sqlite3
import statistics

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE sale (region TEXT, month INTEGER, amount REAL)")
conn.executemany("INSERT INTO sale VALUES (?, ?, ?)", [
    ("norte", 1, 100), ("norte", 2, 120), ("norte", 3, 90), ("sul", 1, 200), ("sul", 2, 210), ("sul", 3, 250)])

print("função de janela (soma acumulada e posição por região):")
for row in conn.execute("""
    SELECT region, month, amount,
           SUM(amount) OVER (PARTITION BY region ORDER BY month) AS running,
           RANK() OVER (PARTITION BY month ORDER BY amount DESC) AS rank_in_month
    FROM sale ORDER BY region, month"""):
    print("  ", row)

print("CTE recursiva (hierarquia e sequência):")
conn.execute("CREATE TABLE employee (id INTEGER PRIMARY KEY, name TEXT, boss_id INTEGER)")
conn.executemany("INSERT INTO employee VALUES (?, ?, ?)", [(1, "Diretora", None), (2, "Gerente", 1), (3, "Dev", 2), (4, "Estagiária", 3)])
for row in conn.execute("""
    WITH RECURSIVE chain(id, name, depth) AS (
        SELECT id, name, 0 FROM employee WHERE boss_id IS NULL
        UNION ALL
        SELECT e.id, e.name, c.depth + 1 FROM employee e JOIN chain c ON e.boss_id = c.id)
    SELECT depth, name FROM chain ORDER BY depth"""):
    print("  ", "  " * row[0] + row[1])

print("JSON dentro do banco:")
conn.execute("CREATE TABLE doc (id INTEGER PRIMARY KEY, data TEXT NOT NULL CHECK (json_valid(data)))")
conn.execute("INSERT INTO doc (data) VALUES (?)", ('{"user": {"name": "Ana", "tags": ["a", "b"]}, "score": 9.5}',))
print("  ", conn.execute("SELECT data ->> '$.user.name', data -> '$.user.tags', json_extract(data, '$.score') FROM doc").fetchone())

print("busca de texto completo (FTS5):")
conn.execute("CREATE VIRTUAL TABLE article USING fts5(title, body)")
conn.executemany("INSERT INTO article VALUES (?, ?)", [
    ("Python 3.15", "novidades do interpretador e do free-threading"),
    ("SQLite", "um banco de dados embutido, simples e rápido"),
    ("Receita", "bolo de cenoura com cobertura de chocolate")])
print("  ", conn.execute("SELECT title FROM article WHERE article MATCH ? ORDER BY rank", ("banco OR interpretador",)).fetchall())

print("funções escritas em Python, chamadas no SQL:")
conn.create_function("slug", 1, lambda s: s.lower().replace(" ", "-"), deterministic=True)


class Median:
    def __init__(self):
        self.values = []

    def step(self, value):
        self.values.append(value)

    def finalize(self):
        return statistics.median(self.values)


conn.create_aggregate("median", 1, Median)
print("  ", conn.execute("SELECT slug('Python Para Todos')").fetchone(), conn.execute("SELECT region, median(amount) FROM sale GROUP BY region").fetchall())
