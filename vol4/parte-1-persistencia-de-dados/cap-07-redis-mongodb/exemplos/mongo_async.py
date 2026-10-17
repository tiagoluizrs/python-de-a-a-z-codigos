"""pymongo assíncrono (AsyncMongoClient, nativo desde o pymongo 4.13)."""
import asyncio
import time

from pymongo import AsyncMongoClient

from dbenv import MONGO_URL


async def main():
    client = AsyncMongoClient(MONGO_URL, tz_aware=True)
    await client.drop_database("livro_demo")
    products = client["livro_demo"]["product"]
    await products.insert_many([{"name": f"p{i}", "stock": i} for i in range(1_000)])
    print("contagem:", await products.count_documents({"stock": {"$gte": 500}}))

    async def one(i):
        return await products.find_one({"name": f"p{i}"})

    start = time.perf_counter()
    docs = await asyncio.gather(*(one(i) for i in range(200)))
    print(f"200 consultas concorrentes: {(time.perf_counter() - start) * 1e3:.0f} ms | achou todas: {all(docs)}")

    async for doc in products.find({"stock": {"$lt": 3}}).sort("stock"):
        print("  async for:", doc["name"])
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$stock"}}}]
    print("agregação:", await (await products.aggregate(pipeline)).to_list())
    await client.drop_database("livro_demo")
    await client.close()


asyncio.run(main())

# para TESTES sem servidor: mongomock
import mongomock

fake = mongomock.MongoClient()["t"]["c"]
fake.insert_many([{"x": 1}, {"x": 2}])
print("mongomock:", fake.count_documents({"x": {"$gt": 1}}), "(cobre CRUD e consultas comuns; NÃO simula índices, transações nem o desempenho)")
