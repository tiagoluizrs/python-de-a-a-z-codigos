"""Quatro bibliotecas de filas (RQ, Dramatiq, Huey, Celery) medidas lado a lado, com workers em contêineres Linux.

    python exemplos/queue_lab.py                # tudo
    python exemplos/queue_lab.py throughput crash

Precisa do Docker. A imagem ``tasks-lab`` (exemplos/tasks_lab) é construída na primeira execução.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import redis

HERE = Path(__file__).parent
LAB = HERE / "tasks_lab"
PORT = 56379
NETWORK = "lab-net"
os.environ["REDIS_URL"] = f"redis://localhost:{PORT}/0"
sys.path.insert(0, str(LAB))

WORKER_CMDS = {
    "rq": lambda c: f"rq worker-pool -n {c} -u redis://lab-redis:6379/0 default",
    "dramatiq": lambda c: f"dramatiq dramatiq_tasks --processes 1 --threads {c}",
    "huey": lambda c: f"huey_consumer huey_tasks.huey -w {c} -k thread",
    "celery": lambda c: f"celery -A celery_tasks worker --concurrency={c} --pool={os.environ.get('CELERY_POOL', 'prefork')} -l info",
}


def docker(*args, check=True):
    return subprocess.run(["docker", *args], capture_output=True, text=True, check=check, encoding="utf-8")


def setup():
    docker("build", "-q", "-t", "tasks-lab", str(LAB))
    docker("network", "create", NETWORK, check=False)
    docker("rm", "-f", "lab-redis", check=False)
    docker("run", "-d", "--name", "lab-redis", "--network", NETWORK, "-p", f"127.0.0.1:{PORT}:6379", "redis:8-alpine")
    r = redis.Redis(port=PORT, decode_responses=True)
    for _ in range(50):
        try:
            r.ping()
            return r
        except redis.ConnectionError:
            time.sleep(0.1)
    raise RuntimeError("Redis não subiu")


def teardown():
    docker("rm", "-f", "lab-redis", check=False)
    for name in docker("ps", "-aq", "--filter", "name=lab-worker").stdout.split():
        docker("rm", "-f", name, check=False)
    docker("network", "rm", NETWORK, check=False)


def start_worker(lib: str, concurrency: int, name: str | None = None, extra_env=()):
    name = name or f"lab-worker-{lib}"
    docker("rm", "-f", name, check=False)
    env = ["-e", "REDIS_URL=redis://lab-redis:6379/0", *extra_env]
    docker("run", "-d", "--name", name, "--network", NETWORK, *env, "tasks-lab", "sh", "-c", WORKER_CMDS[lib](concurrency))
    return name


def stop_worker(name: str):
    docker("rm", "-f", name, check=False)


def wait_ready(lib: str, name: str, timeout=30.0):
    """Espera o worker dizer que está pronto (cada biblioteca anuncia de um jeito)."""
    markers = {"rq": "Listening", "dramatiq": "Worker process is ready", "huey": "Huey consumer started", "celery": "ready."}
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        logs = docker("logs", name, check=False)
        text = logs.stdout + logs.stderr
        if markers[lib].lower() in text.lower():
            return time.perf_counter() - start
        time.sleep(0.2)
    raise TimeoutError(f"{lib}: worker não ficou pronto\n{text[-500:]}")


def producers():
    import celery_tasks
    import common
    import dramatiq_tasks
    import huey_tasks
    from rq import Queue

    queue = Queue(connection=redis.Redis(port=PORT))
    return {
        "rq": {"io": lambda i, ms: queue.enqueue(common.io_task, i, ms), "cpu": lambda n: queue.enqueue(common.cpu_task, n),
               "flaky": lambda i: queue.enqueue(common.flaky_task, i, retry=__import__("rq").Retry(max=5, interval=0))},
        "dramatiq": {"io": dramatiq_tasks.io_task.send, "cpu": dramatiq_tasks.cpu_task.send, "flaky": dramatiq_tasks.flaky_task.send},
        "huey": {"io": huey_tasks.io_task, "cpu": huey_tasks.cpu_task, "flaky": huey_tasks.flaky_task},
        "celery": {"io": celery_tasks.io_task.delay, "cpu": celery_tasks.cpu_task.delay, "flaky": celery_tasks.flaky_task.delay},
    }


def wait_done(r, target: int, timeout: float) -> float:
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        if int(r.get("done") or 0) >= target:
            return time.perf_counter() - start
        time.sleep(0.02)
    return float("nan")


def section_throughput(r, libs):
    print("== VAZÃO: 400 tarefas de E/S de 50 ms (ideal = 400 x 50 ms / concorrência) ==")
    n, ms = 400, 50
    print(f"  {'biblioteca':<10} {'conc.':>5} | {'enfileirar':>14} | {'esvaziar':>9} | {'tarefas/s':>9} | {'ideal':>7} | eficiência")
    for lib in libs:
        for concurrency in (1, 4, 16):
            r.flushall()
            name = start_worker(lib, concurrency)
            wait_ready(lib, name)
            prod = producers()[lib]
            start = time.perf_counter()
            for i in range(n):
                prod["io"](f"t{i}", ms)
            t_enqueue = time.perf_counter() - start
            t_drain = wait_done(r, n, 120)
            total = t_enqueue + t_drain if t_drain == t_drain else float("nan")
            ideal = n * ms / 1000 / concurrency
            end_to_end = time.perf_counter() - start
            print(f"  {lib:<10} {concurrency:>5} | {n / t_enqueue:7,.0f} /s     | {end_to_end:7.2f} s | {n / end_to_end:9.1f} | {ideal:6.2f}s | {ideal / end_to_end:5.0%}")
            stop_worker(name)


def section_cpu(r):
    print("\n== CPU: 150 tarefas de fib(25) ~ 15 ms cada; threads (GIL) x processos (Dramatiq) ==")
    n = 150
    for label, procs, threads in (("1 processo x 1 thread", 1, 1), ("1 processo x 4 threads", 1, 4), ("4 processos x 1 thread", 4, 1)):
        r.flushall()
        name = "lab-worker-cpu"
        docker("rm", "-f", name, check=False)
        docker("run", "-d", "--name", name, "--network", NETWORK, "-e", "REDIS_URL=redis://lab-redis:6379/0", "tasks-lab", "sh", "-c",
               f"dramatiq dramatiq_tasks --processes {procs} --threads {threads}")
        wait_ready("dramatiq", name)
        time.sleep(1.0)
        prod = producers()["dramatiq"]
        start = time.perf_counter()
        for _ in range(n):
            prod["cpu"](25)
        wait_done(r, n, 120)
        print(f"  {label:<24} {time.perf_counter() - start:6.2f} s")
        stop_worker(name)


def section_retries(r, libs):
    print("\n== NOVAS TENTATIVAS: 20 tarefas que falham 2 vezes e funcionam na 3ª ==")
    for lib in libs:
        r.flushall()
        name = start_worker(lib, 4)
        wait_ready(lib, name)
        prod = producers()[lib]
        for i in range(20):
            prod["flaky"](f"f{i}")
        t = wait_done(r, 20, 60)
        attempts = sum(int(v) for v in r.hvals("attempts"))
        print(f"  {lib:<10} concluídas: {int(r.get('done') or 0):>2}/20 | tentativas totais: {attempts:>3} (esperado 60) | tempo {t:5.2f} s")
        stop_worker(name)


def section_crash(r, libs, tuned=False):
    mode = "AJUSTADA (celery: acks_late + prefetch 1 + visibility 10 s; dramatiq: heartbeat 5 s)" if tuned else "PADRÃO"
    print(f"\n== QUEDA DO WORKER, configuração {mode}: 24 tarefas de 1 s, 4 threads; contêiner MORTO (SIGKILL) aos 2,5 s; um novo worker sobe ==")
    n = 24
    for lib in libs:
        r.flushall()
        extra = ("-e", "TUNED=1") if tuned else ()
        name = start_worker(lib, 4, extra_env=extra)
        wait_ready(lib, name)
        prod = producers()[lib]
        for i in range(n):
            prod["io"](f"c{i}", 1000)
        time.sleep(2.5)
        done_before = int(r.get("done") or 0)
        docker("kill", name)
        stop_worker(name)
        name = start_worker(lib, 4, name=f"lab-worker-{lib}-2", extra_env=extra)
        wait_ready(lib, name)
        limit = int(os.environ.get("QUEUE_LAB_CRASH_WAIT", 40 if tuned else 25))
        start_wait, k = time.perf_counter(), 0
        while time.perf_counter() - start_wait < limit:
            if all(f"c{i}" in r.hgetall("runs") for i in range(n)):
                break
            if tuned and lib == "dramatiq" and k % 4 == 0:
                prod["io"](f"nudge{k}", 10)             # um fio de tráfego: a faxina do Dramatiq só roda quando há movimento
            k += 1
            time.sleep(0.5)
        time.sleep(1.5)
        done = int(r.get("done") or 0)
        runs = r.hgetall("runs")
        lost = [f"c{i}" for i in range(n) if f"c{i}" not in runs]
        dup = sum(1 for v in runs.values() if int(v) > 1)
        print(f"  {lib:<10} feitas antes da queda: {done_before:>2} | no fim: {done:>2}/{n} | PERDIDAS: {len(lost):>2} | executadas 2 vezes: {dup}")
        stop_worker(name)


SECTIONS = ["throughput", "cpu", "retries", "crash", "crash-tuned"]

if __name__ == "__main__":
    chosen = sys.argv[1:] or SECTIONS
    libs = os.environ.get("QUEUE_LAB_LIBS", "rq,dramatiq,huey,celery").split(",")
    r = setup()
    try:
        if "throughput" in chosen:
            section_throughput(r, libs)
        if "cpu" in chosen:
            section_cpu(r)
        if "retries" in chosen:
            section_retries(r, libs)
        if "crash" in chosen:
            section_crash(r, libs)
        if "crash-tuned" in chosen:
            section_crash(r, libs, tuned=True)
    finally:
        teardown()
