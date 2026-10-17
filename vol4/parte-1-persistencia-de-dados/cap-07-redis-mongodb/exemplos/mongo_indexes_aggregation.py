"""Índices, EXPLAIN e o pipeline de agregação."""
import time

import pymongo

from dbenv import MONGO_URL

client = pymongo.MongoClient(MONGO_URL, tz_aware=True)
client.drop_database("livro_demo")
db = client["livro_demo"]
sales = db["sale"]
N = 200_000
sales.insert_many([{"customer": f"c{i % 5000}", "category": ["livros", "jogos", "roupas", "casa"][i % 4], "amount": (i % 97) + 1, "n": i} for i in range(N)])
print(f"{N:,} documentos")


def stage(explain):
    node = explain["queryPlanner"]["winningPlan"]
    names = []
    while node:
        names.append(node["stage"])
        node = node.get("inputStage")
    return " > ".join(names)


query = {"n": 150_000}
print("sem índice :", stage(sales.find(query).explain()), end="")
start = time.perf_counter()
sales.find_one(query)
no_index = time.perf_counter() - start
print(f" | {no_index * 1e3:.1f} ms")
sales.create_index("n")
print("com índice :", stage(sales.find(query).explain()), end="")
start = time.perf_counter()
for _ in range(200):
    sales.find_one(query)
with_index = (time.perf_counter() - start) / 200
print(f" | {with_index * 1e3:.2f} ms | {no_index / with_index:,.0f}x mais rápido")

# o índice composto serve a consultas por prefixo
sales.create_index([("category", 1), ("amount", -1)])
print("composto (category, amount):", stage(sales.find({"category": "livros"}).sort("amount", -1).explain()), "(a ordenação também sai do índice)")

# pipeline de agregação: $match -> $group -> $sort -> $limit
pipeline = [
    {"$match": {"amount": {"$gte": 50}}},
    {"$group": {"_id": "$category", "total": {"$sum": "$amount"}, "pedidos": {"$sum": 1}, "media": {"$avg": "$amount"}}},
    {"$sort": {"total": -1}},
]
start = time.perf_counter()
rows = list(sales.aggregate(pipeline))
print(f"agregação em {(time.perf_counter() - start) * 1e3:.0f} ms:")
for row in rows:
    print(f"   {row['_id']:<8} total={row['total']:>9,} pedidos={row['pedidos']:>6,} média={row['media']:.1f}")
print("   (SQL equivalente: SELECT category, SUM(amount), COUNT(*), AVG(amount) FROM sale WHERE amount >= 50 GROUP BY category ORDER BY 2 DESC)")

# $lookup: o JOIN do MongoDB (caro: prefira embutir, veja mongo_modeling)
db["customer"].insert_many([{"_id": f"c{i}", "name": f"Cliente {i}"} for i in range(5000)])
joined = list(sales.aggregate([{"$match": {"n": {"$lt": 3}}}, {"$lookup": {"from": "customer", "localField": "customer", "foreignField": "_id", "as": "cliente"}},
                               {"$project": {"_id": 0, "n": 1, "cliente.name": 1}}]))
print("$lookup:", joined)

# TTL: o próprio banco apaga documentos expirados
import datetime as dt

db["session"].create_index("expires", expireAfterSeconds=0)
db["session"].insert_one({"user": "ana", "expires": dt.datetime.now(dt.UTC) + dt.timedelta(seconds=1)})
print("TTL index criado: o MongoDB remove 'session' após 'expires' (o monitor roda a cada 60 s)")
client.drop_database("livro_demo")
