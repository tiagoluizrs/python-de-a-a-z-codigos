"""Normalização: por que repetir dados cria anomalias (SQLite em memória)."""
import sqlite3

conn = sqlite3.connect(":memory:")

# desnormalizado: o cliente e a cidade se repetem em cada pedido
conn.execute("CREATE TABLE order_flat (id INTEGER PRIMARY KEY, customer_id INTEGER, customer_name TEXT, customer_city TEXT, product TEXT, total REAL)")
conn.executemany("INSERT INTO order_flat (customer_id, customer_name, customer_city, product, total) VALUES (?, ?, ?, ?, ?)",
                 [(1, "Ana", "Recife", f"produto {i}", 10.0 + i) for i in range(1000)] + [(2, "Bia", "Natal", "produto x", 5.0)])

print("1) ANOMALIA DE ATUALIZAÇÃO: a Ana se mudou, e a aplicação atualiza só os pedidos de hoje:")
conn.execute("UPDATE order_flat SET customer_city = 'Olinda' WHERE customer_id = 1 AND id <= 400")      # esqueceu de 600 linhas
cities = conn.execute("SELECT customer_city, COUNT(*) FROM order_flat WHERE customer_id = 1 GROUP BY 1 ORDER BY 2 DESC").fetchall()
print("   cidades da Ana:", cities, "<- DUAS verdades para o mesmo cliente")

print("2) ANOMALIA DE EXCLUSÃO: ao apagar o único pedido da Bia, perdemos o cadastro dela:")
conn.execute("DELETE FROM order_flat WHERE customer_id = 2")
print("   a Bia ainda existe?", conn.execute("SELECT COUNT(*) FROM order_flat WHERE customer_name = 'Bia'").fetchone()[0] > 0)

print("3) ANOMALIA DE INSERÇÃO: não dá para cadastrar um cliente que ainda não comprou (o pedido é obrigatório na mesma linha)")

# 3FN: cada fato em UM lugar
conn.executescript("""
CREATE TABLE customer (id INTEGER PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL);
CREATE TABLE sale (id INTEGER PRIMARY KEY, customer_id INTEGER NOT NULL REFERENCES customer(id), product TEXT NOT NULL, total NUMERIC NOT NULL);
CREATE INDEX ix_sale_customer ON sale(customer_id);
INSERT INTO customer VALUES (1, 'Ana', 'Recife'), (2, 'Bia', 'Natal');
""")
conn.executemany("INSERT INTO sale (customer_id, product, total) VALUES (1, ?, ?)", [(f"produto {i}", 10.0 + i) for i in range(1000)])
print("\nnormalizado (3FN):")
conn.execute("UPDATE customer SET city = 'Olinda' WHERE id = 1")
print("   UMA linha atualizada; todos os 1000 pedidos 'enxergam' a nova cidade:", conn.execute(
    "SELECT c.city, COUNT(*) FROM sale s JOIN customer c ON c.id = s.customer_id GROUP BY 1").fetchall())
print("   Bia continua cadastrada sem pedidos:", conn.execute("SELECT name FROM customer WHERE id = 2").fetchone())

flat = conn.execute("SELECT SUM(LENGTH(customer_name) + LENGTH(customer_city)) FROM order_flat").fetchone()[0]
print(f"\nbytes de texto repetidos nos pedidos (desnormalizado): {flat:,} contra 0 (normalizado, só no cliente)")
print("Quando DESNORMALIZAR de propósito: relatórios/consultas muito lidas e pouco escritas (um total pré-calculado, um nome do cliente")
print("copiado no pedido para fixar o 'nome na data da compra'). A regra: normalize primeiro; desnormalize com MEDIDA e com um dono da consistência.")
