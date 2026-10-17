"""MongoDB: documentos, CRUD, operadores de atualização, tipos."""
import datetime as dt
import decimal
import uuid

import pymongo
from bson import Decimal128, ObjectId
from bson.binary import UuidRepresentation

from dbenv import MONGO_URL

client = pymongo.MongoClient(MONGO_URL, tz_aware=True)        # tz_aware: datetimes COM fuso (sem isso voltam ingênuos)
print("pymongo", pymongo.version, "| servidor", client.server_info()["version"])
client.drop_database("livro_demo")
products = client["livro_demo"]["product"]

# inserir: o banco cria o _id (ObjectId) e a coleção, sem esquema
result = products.insert_one({"name": "caneta", "price": Decimal128("9.90"), "tags": ["papelaria", "azul"], "dims": {"w": 1, "h": 14},
                              "created": dt.datetime(2026, 10, 7, 9, 30, tzinfo=dt.UTC)})
print("_id:", result.inserted_id, type(result.inserted_id).__name__, "| nasceu em", result.inserted_id.generation_time.isoformat())
products.insert_many([{"name": f"p{i}", "price": Decimal128(str(i)), "stock": i * 10, "cat": "a" if i % 2 else "b"} for i in range(1, 7)])

# consultar
doc = products.find_one({"name": "caneta"})
print("documento:", {k: v for k, v in doc.items() if k != "_id"})
print("Decimal128 -> Decimal:", doc["price"].to_decimal(), "| datetime com fuso:", doc["created"].tzinfo)
print("projeção:", list(products.find({"cat": "a"}, {"_id": 0, "name": 1, "stock": 1}).sort("stock", -1).limit(2)))
print("operadores:", products.count_documents({"stock": {"$gte": 30, "$lt": 60}}), "docs com 30 <= stock < 60 | $or:", products.count_documents({"$or": [{"cat": "a"}, {"name": "caneta"}]}))
print("campo aninhado e array:", products.count_documents({"dims.w": 1}), products.count_documents({"tags": "azul"}))

# atualizar: SEMPRE com operadores ($set, $inc, $push...), nunca substituindo o documento sem querer
products.update_one({"name": "p1"}, {"$inc": {"stock": -3}, "$set": {"vip": True}})
products.update_one({"name": "caneta"}, {"$push": {"tags": "nova"}, "$set": {"dims.h": 15}})
print("depois de $inc/$set/$push:", products.find_one({"name": "p1"}, {"_id": 0, "stock": 1, "vip": 1}), products.find_one({"name": "caneta"}, {"_id": 0, "tags": 1, "dims": 1}))
print("upsert:", products.update_one({"name": "novo"}, {"$setOnInsert": {"stock": 1}}, upsert=True).upserted_id is not None, "(cria se não existir)")

# erros e restrições: só existem se você os criar (índice único)
products.create_index("sku", unique=True, sparse=True)
products.insert_one({"name": "x", "sku": "A1"})
try:
    products.insert_one({"name": "y", "sku": "A1"})
except pymongo.errors.DuplicateKeyError as error:
    print("DuplicateKeyError, código", error.code)

# armadilhas dos tipos
try:
    products.insert_one({"id": uuid.uuid4()})
except ValueError as error:
    print("UUID sem configuração:", str(error)[:60], "...")
standard = pymongo.MongoClient(MONGO_URL, uuidRepresentation="standard")["livro_demo"]["uuids"]
value = uuid.uuid4()
standard.insert_one({"u": value})
print("com uuidRepresentation='standard':", standard.find_one()["u"] == value)
try:
    products.insert_one({"price": decimal.Decimal("1.5")})
except Exception as error:
    print("decimal.Decimal direto:", type(error).__name__, "- use bson.Decimal128")

# em lote
ops = [pymongo.UpdateOne({"name": f"p{i}"}, {"$set": {"promo": True}}) for i in range(1, 4)] + [pymongo.DeleteOne({"name": "p6"})]
bulk = products.bulk_write(ops)
print("bulk_write:", bulk.modified_count, "atualizados,", bulk.deleted_count, "removido")
client.drop_database("livro_demo")
