"""Conectar, criar, inserir com parâmetros, consultar."""
import sqlite3

print("versão do SQLite embutida:", sqlite3.sqlite_version, "| threadsafety:", sqlite3.threadsafety)

conn = sqlite3.connect(":memory:")                  # um banco só na memória; um arquivo: connect("loja.db")
conn.execute("CREATE TABLE product (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL NOT NULL, category TEXT)")

# SEMPRE parâmetros (?), nunca f-string com valores
conn.execute("INSERT INTO product (name, price, category) VALUES (?, ?, ?)", ("caneta", 2.5, "papelaria"))
conn.executemany(
    "INSERT INTO product (name, price, category) VALUES (:name, :price, :category)",
    [{"name": "caderno", "price": 18.9, "category": "papelaria"}, {"name": "mochila", "price": 120.0, "category": "bolsas"}],
)
conn.commit()

print("fetchall :", conn.execute("SELECT id, name, price FROM product ORDER BY id").fetchall())
print("fetchone :", conn.execute("SELECT name FROM product WHERE id = ?", (2,)).fetchone())
print("escalar  :", conn.execute("SELECT COUNT(*) FROM product").fetchone()[0])

# o cursor é iterável: não carrega tudo na memória
for name, price in conn.execute("SELECT name, price FROM product WHERE price > ?", (10,)):
    print("  caro:", name, price)

# Row: acesso por nome
conn.row_factory = sqlite3.Row
row = conn.execute("SELECT * FROM product WHERE name = ?", ("mochila",)).fetchone()
print("Row:", row["name"], row["price"], "| colunas:", row.keys(), "| dict:", dict(row))

# cursor.lastrowid e rowcount
cursor = conn.execute("INSERT INTO product (name, price) VALUES (?, ?)", ("lápis", 1.0))
print("lastrowid:", cursor.lastrowid, "| rowcount do UPDATE:", conn.execute("UPDATE product SET price = price * 1.1 WHERE category = ?", ("papelaria",)).rowcount)
conn.close()
