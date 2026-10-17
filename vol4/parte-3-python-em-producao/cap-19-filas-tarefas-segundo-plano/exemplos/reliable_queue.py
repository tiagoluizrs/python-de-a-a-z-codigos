"""Uma fila CONFIÁVEL sobre o Redis, escrita à mão para entender o que as bibliotecas fazem: confirmação, prazo de visibilidade,
novas tentativas com espera exponencial e jitter, fila de mensagens mortas e idempotência.

Precisa de um Redis em localhost:56380 (``docker run -d --name q71-redis -p 127.0.0.1:56380:6379 redis:8-alpine``); o
próprio exemplo sobe e derruba esse contêiner se ele não existir.
"""
import json
import random
import subprocess
import time
import uuid

import redis

PORT = 56380

# Os scripts Lua rodam ATÔMICOS no Redis: sem eles, uma queda entre dois comandos perderia a mensagem.
CLAIM = """
local id = redis.call('RPOP', KEYS[1])
if not id then return nil end
redis.call('ZADD', KEYS[2], ARGV[1], id)
return id
"""
REAP = """
local expired = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ARGV[1])
for _, id in ipairs(expired) do
    redis.call('ZREM', KEYS[1], id)
    redis.call('LPUSH', KEYS[2], id)
    redis.call('HINCRBY', KEYS[3], id, 1)
end
return #expired
"""
PROMOTE = """
local due = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ARGV[1])
for _, id in ipairs(due) do
    redis.call('ZREM', KEYS[1], id)
    redis.call('LPUSH', KEYS[2], id)
end
return #due
"""


class ReliableQueue:
    def __init__(self, r: redis.Redis, name="q", visibility=30.0, max_attempts=3, base_delay=0.5, max_delay=30.0):
        self.r, self.name = r, name
        self.visibility, self.max_attempts, self.base_delay, self.max_delay = visibility, max_attempts, base_delay, max_delay
        self._claim, self._reap, self._promote = r.register_script(CLAIM), r.register_script(REAP), r.register_script(PROMOTE)
        self.ready, self.inflight, self.delayed, self.dead = f"{name}:ready", f"{name}:inflight", f"{name}:delayed", f"{name}:dead"

    def put(self, payload: dict, delay: float = 0.0) -> str:
        msg_id = uuid.uuid4().hex[:10]
        pipe = self.r.pipeline()
        pipe.hset(f"{self.name}:msg:{msg_id}", mapping={"payload": json.dumps(payload)})
        if delay:
            pipe.zadd(self.delayed, {msg_id: time.time() + delay})
        else:
            pipe.lpush(self.ready, msg_id)
        pipe.execute()
        return msg_id

    def get(self):
        """Pega UMA mensagem e a deixa 'em processamento' até o prazo de visibilidade; devolve (id, payload) ou None."""
        self._promote(keys=[self.delayed, self.ready], args=[time.time()])
        msg_id = self._claim(keys=[self.ready, self.inflight], args=[time.time() + self.visibility])
        if msg_id is None:
            return None
        return msg_id, json.loads(self.r.hget(f"{self.name}:msg:{msg_id}", "payload"))

    def ack(self, msg_id: str) -> None:
        """Terminou: só agora a mensagem sai de verdade."""
        pipe = self.r.pipeline()
        pipe.zrem(self.inflight, msg_id)
        pipe.delete(f"{self.name}:msg:{msg_id}")
        pipe.execute()

    def nack(self, msg_id: str) -> float | None:
        """Falhou: agenda nova tentativa com espera exponencial e jitter, ou manda para a fila de mortas. Devolve a espera."""
        attempts = self.r.hincrby(f"{self.name}:attempts", msg_id, 1)
        self.r.zrem(self.inflight, msg_id)
        if attempts >= self.max_attempts:
            self.r.lpush(self.dead, msg_id)
            return None
        delay = min(self.base_delay * 2 ** (attempts - 1), self.max_delay)
        delay = random.uniform(0, delay)                                  # "full jitter": evita que todos tentem juntos
        self.r.zadd(self.delayed, {msg_id: time.time() + delay})
        return delay

    def reap(self) -> int:
        """Devolve à fila as mensagens cujo prazo venceu (o worker que as pegou caiu ou travou)."""
        return self._reap(keys=[self.inflight, self.ready, f"{self.name}:attempts"], args=[time.time()])

    def sizes(self) -> dict:
        return {"ready": self.r.llen(self.ready), "inflight": self.r.zcard(self.inflight), "delayed": self.r.zcard(self.delayed), "dead": self.r.llen(self.dead)}


def connect() -> tuple[redis.Redis, bool]:
    r = redis.Redis(port=PORT, decode_responses=True)
    started = False
    try:
        r.ping()
    except redis.ConnectionError:
        subprocess.run(["docker", "rm", "-f", "q71-redis"], capture_output=True)
        subprocess.run(["docker", "run", "-d", "--name", "q71-redis", "-p", f"127.0.0.1:{PORT}:6379", "redis:8-alpine"], capture_output=True, check=True)
        started = True
        for _ in range(50):
            try:
                r.ping()
                break
            except redis.ConnectionError:
                time.sleep(0.1)
    r.flushall()
    return r, started


if __name__ == "__main__":
    r, started = connect()
    try:
        # 1. o fluxo normal: pegar, processar, confirmar
        q = ReliableQueue(r, visibility=1.0)
        for i in range(3):
            q.put({"n": i})
        print("fila:", q.sizes())
        msg_id, payload = q.get()
        print(f"pegou {payload} -> em processamento: {q.sizes()}")
        q.ack(msg_id)
        print("confirmou:", q.sizes())

        # 2. o worker CAI sem confirmar: a mensagem não se perde, volta depois do prazo (e vai executar de novo)
        q.get()                                                          # pega a 2ª mensagem e "morre" (nunca chama ack)
        print(f"\nworker caiu com 1 mensagem em processamento: {q.sizes()} | reap agora devolve {q.reap()} (o prazo ainda não venceu)")
        time.sleep(1.2)
        print(f"depois de {q.visibility}s de prazo: reap devolve {q.reap()} -> {q.sizes()}")
        print("as mensagens de volta executam DE NOVO: entrega 'pelo menos uma vez' (at-least-once)")

        # 3. idempotência: executar duas vezes não pode cobrar duas vezes
        effects = []

        def handle(payload, msg_id):
            if not r.set(f"done:{payload['order']}", msg_id, nx=True):      # SET NX: a primeira execução vence
                return "duplicada, ignorada"
            effects.append(payload["order"])                                  # o efeito (cobrar, enviar e-mail) acontece UMA vez
            return "executada"

        q2 = ReliableQueue(r, name="pay", visibility=0.3)
        q2.put({"order": "A-1"})
        mid, payload = q2.get()
        first = handle(payload, mid)                                          # processou... e o worker caiu ANTES do ack
        time.sleep(0.4)
        q2.reap()
        mid, payload = q2.get()
        second = handle(payload, mid)
        q2.ack(mid)
        print(f"\nidempotência: 1ª execução {first!r} | reentrega {second!r} | efeitos reais: {effects}")

        # 4. tarefa venenosa: falha sempre; após N tentativas vai para a fila de mortas (DLQ) em vez de travar tudo
        q3 = ReliableQueue(r, name="poison", max_attempts=3, base_delay=0.05, visibility=5)
        q3.put({"bad": True})
        q3.put({"good": True})
        delays = []
        deadline = time.time() + 5
        while time.time() < deadline and (q3.sizes()["ready"] or q3.sizes()["delayed"] or q3.sizes()["inflight"]):
            item = q3.get()
            if item is None:
                time.sleep(0.01)
                continue
            mid, payload = item
            if payload.get("bad"):
                delays.append(q3.nack(mid))
            else:
                q3.ack(mid)
        print(f"\nveneno: tentativas e esperas (jitter) {[round(d, 3) if d is not None else 'DLQ' for d in delays]} | filas: {q3.sizes()}")
        print("a tarefa boa NÃO ficou presa atrás da venenosa; a venenosa foi isolada para uma pessoa olhar")

        # 5. a espera exponencial com jitter
        q4 = ReliableQueue(r, name="b", base_delay=1.0, max_delay=30.0)
        print("\nteto da espera por tentativa (base 1 s, teto 30 s):", [min(1.0 * 2 ** k, 30.0) for k in range(8)], "| com jitter cada uma sorteia em [0, teto]")

        # 6. custo
        q5 = ReliableQueue(r, name="bench", visibility=30)
        n = 5000
        start = time.perf_counter()
        for i in range(n):
            q5.put({"i": i})
        t_put = time.perf_counter() - start
        start = time.perf_counter()
        for _ in range(n):
            mid, _ = q5.get()
            q5.ack(mid)
        t_get = time.perf_counter() - start
        print(f"\n{n:,} mensagens: put {n / t_put:7,.0f}/s | get+ack {n / t_get:7,.0f}/s (cada ida e volta ao Redis custa ~{t_get / n / 3 * 1e6:.0f} µs)")
    finally:
        if started:
            subprocess.run(["docker", "rm", "-f", "q71-redis"], capture_output=True)
