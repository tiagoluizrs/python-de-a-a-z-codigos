"""Redis: os tipos de dados, TTL, pipelines e SCAN."""
import time

import redis

from dbenv import REDIS_URL

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)       # decode_responses: str em vez de bytes
r.flushdb()
print("redis-py", redis.__version__, "| servidor", r.info("server")["redis_version"])

# strings, TTL e contadores atômicos
r.set("nome", "Ana", ex=60)
print("string:", r.get("nome"), "| TTL:", r.ttl("nome"), "s | tipo:", r.type("nome"))
print("INCR:", r.incr("visitas"), r.incr("visitas"), r.incrby("visitas", 10), "(atômico, sem condição de corrida)")
print("chave inexistente:", r.get("nao_existe"), "(None, não erro)")

# hash: um 'objeto' com campos
r.hset("user:1", mapping={"name": "Ana", "age": 30, "city": "Recife"})
print("hash:", r.hgetall("user:1"), "| um campo:", r.hget("user:1", "city"), "| (valores voltam como STR)")
r.hincrby("user:1", "age", 1)

# lista: fila / pilha
r.rpush("fila", "a", "b", "c")
print("lista:", r.lrange("fila", 0, -1), "| lpop:", r.lpop("fila"), "| tamanho:", r.llen("fila"))

# conjunto e conjunto ordenado
r.sadd("tags:1", "python", "redis", "python")
r.sadd("tags:2", "python", "mongo")
print("set (sem repetição):", sorted(r.smembers("tags:1")), "| interseção:", r.sinter("tags:1", "tags:2"))
r.zadd("placar", {"ana": 120, "bia": 340, "caio": 80})
print("zset (ranking):", r.zrevrange("placar", 0, 1, withscores=True), "| posição da ana:", r.zrevrank("placar", "ana") + 1)

# expiração real
r.set("efemero", "x", px=150)
time.sleep(0.25)
print("depois de 250 ms:", r.get("efemero"), "(expirou sozinho)")

# round trips: a latência de rede domina
N = 5_000
start = time.perf_counter()
for i in range(N):
    r.set(f"k{i}", i)
loop = time.perf_counter() - start
start = time.perf_counter()
with r.pipeline(transaction=False) as pipe:
    for i in range(N):
        pipe.set(f"k{i}", i)
    pipe.execute()
piped = time.perf_counter() - start
print(f"{N:,} SET: laço {loop:.2f} s ({loop / N * 1e6:.0f} us cada) | pipeline {piped * 1e3:.0f} ms | {loop / piped:.0f}x mais rápido")

# SCAN (incremental) em vez de KEYS (bloqueia o servidor)
found = sum(1 for _ in r.scan_iter(match="k1*", count=1000))
print(f"SCAN com padrão 'k1*': {found} chaves (KEYS faria o mesmo, mas BLOQUEIA o servidor em bases grandes)")
print("memória usada:", r.info("memory")["used_memory_human"], "| chaves:", r.dbsize())
r.flushdb()
