"""Modelagem (embutir x referenciar), validação, atomicidade e transações."""
import threading
import time

import pymongo

from dbenv import MONGO_URL

client = pymongo.MongoClient(MONGO_URL, tz_aware=True)
client.drop_database("livro_demo")
db = client["livro_demo"]

# 1. embutir x referenciar: o equivalente MongoDB do N+1
db["author"].insert_many([{"_id": i, "name": f"a{i}"} for i in range(500)])
db["book_ref"].insert_many([{"author_id": i, "title": f"b{i}-{j}"} for i in range(500) for j in range(5)])
db["author_emb"].insert_many([{"_id": i, "name": f"a{i}", "books": [{"title": f"b{i}-{j}"} for j in range(5)]} for i in range(500)])

start = time.perf_counter()
total = 0
for author in db["author"].find():
    total += db["book_ref"].count_documents({"author_id": author["_id"]})                # 1 + 500 consultas
referenced = time.perf_counter() - start
start = time.perf_counter()
total2 = sum(len(a["books"]) for a in db["author_emb"].find())                            # 1 consulta
embedded = time.perf_counter() - start
print(f"500 autores x 5 livros: referenciando {referenced * 1e3:.0f} ms (501 consultas) | embutindo {embedded * 1e3:.0f} ms (1 consulta) | {referenced / embedded:.0f}x")
print("regra: embuta o que é LIDO junto e tem tamanho limitado (o documento tem teto de 16 MB); referencie o que cresce sem limite ou é compartilhado")

# 2. validação de esquema: o banco recusa documentos inválidos
db.create_collection("user", validator={"$jsonSchema": {"bsonType": "object", "required": ["email"],
                                                         "properties": {"email": {"bsonType": "string", "pattern": "@"}, "age": {"bsonType": "int", "minimum": 0}}}})
for doc in ({"email": "ana@x.com", "age": 30}, {"name": "sem email"}, {"email": "ana@x.com", "age": -5}):
    try:
        db["user"].insert_one(doc)
        print("aceito :", doc)
    except pymongo.errors.WriteError as error:
        print("recusado:", doc, "-> código", error.code, "(Document failed validation)")

# 3. atomicidade de UM documento: $inc com condição
db["stock"].insert_one({"_id": "caneta", "qty": 50})


def sell_unsafe(counter):
    stock = pymongo.MongoClient(MONGO_URL)["livro_demo"]["stock"]
    for _ in range(10):
        qty = stock.find_one({"_id": "caneta"})["qty"]
        if qty > 0:
            stock.update_one({"_id": "caneta"}, {"$set": {"qty": qty - 1}})              # ler, decidir, escrever: corrida
            counter.append(1)


def sell_safe(counter):
    stock = pymongo.MongoClient(MONGO_URL)["livro_demo"]["stock"]
    for _ in range(10):
        if stock.find_one_and_update({"_id": "caneta", "qty": {"$gt": 0}}, {"$inc": {"qty": -1}}) is not None:
            counter.append(1)


for label, worker in (("ler e gravar (corrida)", sell_unsafe), ("find_one_and_update com $inc e condição", sell_safe)):
    db["stock"].update_one({"_id": "caneta"}, {"$set": {"qty": 50}})
    sold = []
    threads = [threading.Thread(target=worker, args=(sold,)) for _ in range(8)]                # 80 tentativas, só 50 em estoque
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"{label:<44}: vendas {len(sold):>2} de 50 em estoque | estoque final {db['stock'].find_one()['qty']}")

# 4. transações de vários documentos (exigem um conjunto de réplicas; este servidor tem um nó)
db["acc"].insert_many([{"_id": "a", "bal": 100}, {"_id": "b", "bal": 0}])
try:
    with client.start_session() as session:
        with session.start_transaction():
            db["acc"].update_one({"_id": "a"}, {"$inc": {"bal": -30}}, session=session)
            db["acc"].update_one({"_id": "b"}, {"$inc": {"bal": 30}}, session=session)
            raise RuntimeError("falha antes do commit")
except RuntimeError:
    pass
print("transação abortada:", {d["_id"]: d["bal"] for d in db["acc"].find()}, "(nada mudou)")
with client.start_session() as session:
    with session.start_transaction():
        db["acc"].update_one({"_id": "a"}, {"$inc": {"bal": -30}}, session=session)
        db["acc"].update_one({"_id": "b"}, {"$inc": {"bal": 30}}, session=session)
print("transação confirmada:", {d["_id"]: d["bal"] for d in db["acc"].find()})

# 5. change stream: o banco avisa das mudanças (também exige conjunto de réplicas)
events = []


def watch():
    with db["acc"].watch(max_await_time_ms=500) as stream:
        for change in stream:
            events.append((change["operationType"], change.get("documentKey", {}).get("_id")))
            if len(events) >= 2:
                return


watcher = threading.Thread(target=watch)
watcher.start()
time.sleep(0.5)
db["acc"].update_one({"_id": "a"}, {"$set": {"x": 1}})
db["acc"].insert_one({"_id": "c", "bal": 5})
watcher.join(5)
print("change stream:", events)
client.drop_database("livro_demo")
