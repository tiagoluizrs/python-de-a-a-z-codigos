"""Atomicidade no Redis: INCR, Lua, WATCH/MULTI/EXEC e travas."""
import threading
import time
import uuid

import redis

from dbenv import REDIS_URL

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
r.flushdb()


def hammer(worker, threads=8):
    ts = [threading.Thread(target=worker) for _ in range(threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()


# 1. ler-e-escrever (condição de corrida) contra INCR (atômico)
r.set("lido_e_escrito", 0)


def read_modify_write():
    c = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    for _ in range(300):
        c.set("lido_e_escrito", int(c.get("lido_e_escrito")) + 1)


def atomic():
    c = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    for _ in range(300):
        c.incr("incr")


hammer(read_modify_write)
hammer(atomic)
print(f"8 clientes x 300: GET+SET = {r.get('lido_e_escrito')} de 2400 (perdeu incrementos) | INCR = {r.get('incr')} de 2400")

# 2. Lua: o servidor executa o script INTEIRO sem ser interrompido
rate = r.register_script("""
local count = redis.call('INCR', KEYS[1])
if count == 1 then redis.call('PEXPIRE', KEYS[1], ARGV[1]) end
return count
""")
print("script Lua (INCR + EXPIRE só na 1ª vez):", [rate(keys=["janela"], args=[1000]) for _ in range(3)])

# 3. WATCH/MULTI/EXEC: transação otimista (repete se alguém mexeu na chave)
r.set("saldo", 100)


def withdraw(amount):
    with r.pipeline() as pipe:
        while True:
            try:
                pipe.watch("saldo")
                balance = int(pipe.get("saldo"))
                if balance < amount:
                    pipe.unwatch()
                    return False
                pipe.multi()
                pipe.set("saldo", balance - amount)
                pipe.execute()
                return True
            except redis.WatchError:
                continue                                      # alguém alterou 'saldo': tente de novo


results = []
lock = threading.Lock()


def spender():
    c = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    with c.pipeline() as pipe:
        for _ in range(5):
            while True:
                try:
                    pipe.watch("saldo")
                    balance = int(pipe.get("saldo"))
                    if balance < 10:
                        pipe.unwatch()
                        ok = False
                        break
                    pipe.multi()
                    pipe.set("saldo", balance - 10)
                    pipe.execute()
                    ok = True
                    break
                except redis.WatchError:
                    continue
            with lock:
                results.append(ok)


hammer(spender, threads=4)
print(f"WATCH: 20 tentativas de gastar 10 com saldo 100 -> {results.count(True)} deram certo, saldo final {r.get('saldo')} (nunca negativo)")

# 4. trava distribuída: SET NX PX, liberada com um token (só quem a tem a solta)
release = r.register_script("if redis.call('GET', KEYS[1]) == ARGV[1] then return redis.call('DEL', KEYS[1]) else return 0 end")
token = uuid.uuid4().hex
print("1º pega a trava:", r.set("trava", token, nx=True, px=400), "| 2º tenta:", r.set("trava", "outro", nx=True, px=400))
print("outro tenta soltar:", release(keys=["trava"], args=["token-errado"]), "| o dono solta:", release(keys=["trava"], args=[token]))
r.set("trava", "dono-lento", nx=True, px=100)
time.sleep(0.2)
print("trava com TTL expira sozinha (o dono pode morrer sem soltar):", r.get("trava"))
r.flushdb()
