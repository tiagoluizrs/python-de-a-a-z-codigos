"""Padrões com Redis: cache, limite de taxa, ranking, fila confiável, Pub/Sub e Streams."""
import json
import threading
import time

import redis

from dbenv import REDIS_URL

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
r.flushdb()

# 1. cache-aside: lê do cache; se faltar, busca na fonte lenta e guarda com TTL
calls = {"n": 0}


def slow_database(user_id):
    calls["n"] += 1
    time.sleep(0.2)
    return {"id": user_id, "name": f"usuario-{user_id}"}


def get_user(user_id, ttl=30):
    key = f"user:{user_id}"
    cached = r.get(key)
    if cached is not None:
        return json.loads(cached)
    value = slow_database(user_id)
    r.set(key, json.dumps(value), ex=ttl)
    return value


start = time.perf_counter()
get_user(7)
miss = time.perf_counter() - start
start = time.perf_counter()
for _ in range(100):
    get_user(7)
hit = (time.perf_counter() - start) / 100
print(f"cache-aside: miss {miss * 1e3:.0f} ms | hit {hit * 1e3:.2f} ms | {miss / hit:,.0f}x | consultas à fonte: {calls['n']}")

# a manada (cache stampede): muitos pedidos simultâneos de uma chave que acabou de expirar
r.delete("user:9")
calls["n"] = 0
threads = [threading.Thread(target=get_user, args=(9,)) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"stampede: 10 pedidos simultâneos de uma chave fria -> {calls['n']} consultas à fonte (todos acharam o cache vazio)")

# 2. limite de taxa por janela fixa
limiter = r.register_script("local c = redis.call('INCR', KEYS[1]); if c == 1 then redis.call('PEXPIRE', KEYS[1], ARGV[1]) end; return c")
allowed = sum(1 for _ in range(12) if limiter(keys=["rl:ana"], args=[1000]) <= 5)
print(f"limite de 5 por segundo: {allowed} de 12 pedidos permitidos")

# 3. ranking com conjunto ordenado
for member, points in (("ana", 120), ("bia", 340), ("caio", 80), ("dora", 340)):
    r.zadd("ranking", {member: points})
r.zincrby("ranking", 50, "caio")
print("top 3:", r.zrevrange("ranking", 0, 2, withscores=True), "| posição do caio:", r.zrevrank("ranking", "caio") + 1)

# 4. fila CONFIÁVEL: BLMOVE leva o item para uma lista 'em processamento'; ack remove; se o trabalhador morre, recupera
r.rpush("jobs", "job-1", "job-2")
job = r.blmove("jobs", "processando:w1", 1, "LEFT", "RIGHT")
print("trabalhador pegou:", job, "| fila:", r.lrange("jobs", 0, -1), "| em processamento:", r.lrange("processando:w1", 0, -1))
print("o trabalhador MORRE sem confirmar... recuperação:", [r.lmove("processando:w1", "jobs", "RIGHT", "LEFT") for _ in range(r.llen("processando:w1"))], "| fila agora:", r.lrange("jobs", 0, -1))

# 5. Pub/Sub: tempo real, SEM persistência (quem não escuta, perde)
pubsub = r.pubsub()
pubsub.subscribe("avisos")
pubsub.get_message(timeout=1)
r.publish("avisos", "oi")
print("Pub/Sub (assinante ativo):", pubsub.get_message(timeout=1)["data"], "| sem assinante, publish devolve", r.publish("ninguem", "x"), "receptores")

# 6. Streams: um log durável, com grupos de consumidores e confirmação
r.xadd("eventos", {"tipo": "pedido", "id": "1"})
r.xadd("eventos", {"tipo": "pedido", "id": "2"})
r.xgroup_create("eventos", "faturamento", id="0")
messages = r.xreadgroup("faturamento", "c1", {"eventos": ">"}, count=10)[0][1]
print("Stream, lidas pelo grupo:", [fields["id"] for _, fields in messages])
print("pendentes (lidas, não confirmadas):", r.xpending("eventos", "faturamento")["pending"], end=" -> ")
for message_id, _ in messages:
    r.xack("eventos", "faturamento", message_id)
print("após XACK:", r.xpending("eventos", "faturamento")["pending"])
r.flushdb()
