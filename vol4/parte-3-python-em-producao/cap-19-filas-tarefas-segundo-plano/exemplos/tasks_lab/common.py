"""O que as quatro bibliotecas executam: o MESMO trabalho, escrito uma vez."""
import os
import time

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")


def client() -> redis.Redis:
    return redis.Redis.from_url(REDIS_URL, decode_responses=True)


def io_task(task_id: str, ms: int = 50) -> str:
    """Trabalho de E/S (espera): simula uma chamada de rede. Conta a execução em Redis."""
    time.sleep(ms / 1000)
    r = client()
    r.incr("done")
    r.hincrby("runs", task_id, 1)                      # quantas vezes cada tarefa executou (detecta duplicatas)
    return task_id


def cpu_task(n: int = 25) -> int:
    """Trabalho de CPU (Fibonacci recursivo)."""
    def fib(k):
        return k if k < 2 else fib(k - 1) + fib(k - 2)
    value = fib(n)
    client().incr("done")
    return value


def flaky_task(task_id: str) -> str:
    """Falha nas duas primeiras tentativas e funciona na terceira (para exercitar as novas tentativas)."""
    r = client()
    attempt = r.hincrby("attempts", task_id, 1)
    if attempt < 3:
        raise ConnectionError(f"falha {attempt} de {task_id}")
    r.incr("done")
    return f"{task_id} ok na tentativa {attempt}"
