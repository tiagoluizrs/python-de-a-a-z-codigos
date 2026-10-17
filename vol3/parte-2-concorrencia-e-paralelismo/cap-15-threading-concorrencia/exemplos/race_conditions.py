"""Corridas: o mesmo código, com e sem trava, nos dois builds do 3.15."""
import json
import subprocess
import sys
import threading
import time

CODE = """
import json, sys, threading, time

counter = 0

def run(n, fn, threads=8):
    global counter
    counter = 0
    ts = [threading.Thread(target=fn, args=(n,)) for _ in range(threads)]
    for t in ts: t.start()
    for t in ts: t.join()
    return counter

def plain(n):
    global counter
    for _ in range(n):
        counter += 1

def gap(n):
    global counter
    for _ in range(n):
        tmp = counter
        time.sleep(0)            # um ponto onde outra thread pode entrar entre ler e escrever
        counter = tmp + 1

lock = threading.Lock()

def locked(n):
    global counter
    for _ in range(n):
        with lock:
            counter += 1

out = {"gil": sys._is_gil_enabled(),
       "plain": run(200_000, plain), "gap": run(20_000, gap), "locked": run(200_000, locked)}
print(json.dumps(out))
"""


def find_free_threaded():
    result = subprocess.run([sys.executable, "-m", "uv", "python", "find", "3.15+freethreaded"], capture_output=True, text=True)
    return result.stdout.strip() or None


if __name__ == "__main__":
    print("8 threads, cada uma incrementa um contador compartilhado:")
    print(f"{'build':<24}{'sem trava (1,6 mi)':>20}{'com janela (160 mil)':>22}{'com Lock (1,6 mi)':>20}")
    for label, python in [("com GIL", sys.executable), ("sem GIL (3.15t)", find_free_threaded())]:
        if not python:
            print(f"{label:<24} indisponível")
            continue
        out = subprocess.run([python, "-c", CODE], capture_output=True, text=True)
        data = json.loads(out.stdout.strip().splitlines()[-1])
        print(f"{label:<24}{data['plain']:>20,}{data['gap']:>22,}{data['locked']:>20,}")

    # O que a trava custa
    counter = 0
    lock = threading.Lock()

    def plain(n):
        global counter
        for _ in range(n):
            counter += 1

    def locked(n):
        global counter
        for _ in range(n):
            with lock:
                counter += 1

    for label, fn in (("sem trava", plain), ("com Lock", locked)):
        threads = [threading.Thread(target=fn, args=(200_000,)) for _ in range(8)]
        start = time.perf_counter()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        print(f"  {label:<10} 1,6 milhão de incrementos: {time.perf_counter() - start:.2f} s")
