"""Deadlock: dois travam e esperam um pelo outro. Detectar com timeout; evitar com ordem."""
import threading
import time

a, b = threading.Lock(), threading.Lock()
outcome = {}


def take(first, second, name):
    with first:
        time.sleep(0.1)                                          # dá tempo da outra thread pegar o outro
        got = second.acquire(timeout=0.3)                        # SEM timeout, ficaria para sempre
        outcome[name] = got
        if got:
            second.release()


t1 = threading.Thread(target=take, args=(a, b, "t1 (a depois b)"))
t2 = threading.Thread(target=take, args=(b, a, "t2 (b depois a)"))
t1.start()
t2.start()
t1.join()
t2.join()
print("ordens OPOSTAS ->", outcome, "(as duas desistiram: era deadlock)")

# A correção: uma ORDEM GLOBAL para tomar as travas
outcome2 = {}


def take_ordered(first, second, name):
    for lock in sorted((first, second), key=id):               # todos tomam na mesma ordem
        lock.acquire()
    time.sleep(0.1)
    outcome2[name] = True
    for lock in (first, second):
        lock.release()


t1 = threading.Thread(target=take_ordered, args=(a, b, "t1"))
t2 = threading.Thread(target=take_ordered, args=(b, a, "t2"))
start = time.perf_counter()
t1.start()
t2.start()
t1.join()
t2.join()
print(f"mesma ORDEM global ->", outcome2, f"({time.perf_counter() - start:.2f} s, sem deadlock)")

# Ver onde as threads estão presas: o traceback de TODAS as threads
import sys

stuck = threading.Event()
lock = threading.Lock()
lock.acquire()
blocked = threading.Thread(target=lambda: lock.acquire(), name="presa", daemon=True)
blocked.start()
time.sleep(0.1)
frame = sys._current_frames()[blocked.ident]
print("a thread 'presa' está em:", frame.f_code.co_name, "(linha", frame.f_lineno, ") — é o que o faulthandler e os depuradores mostram")
lock.release()
blocked.join()
