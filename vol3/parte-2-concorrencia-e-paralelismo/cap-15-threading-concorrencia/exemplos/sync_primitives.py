"""Os primitivos de sincronização: Lock, RLock, Semaphore, Event, Condition, Barrier."""
import threading
import time
import timeit

# Lock: exclusão mútua
lock = threading.Lock()
print("Lock livre:", lock.acquire(blocking=False), "| de novo (já tomado):", lock.acquire(blocking=False), "| com timeout:", lock.acquire(timeout=0.05))
lock.release()


# RLock: a MESMA thread pode tomar várias vezes (recursão)
rlock = threading.RLock()


def recursive(n):
    with rlock:
        return 1 if n == 0 else 1 + recursive(n - 1)


print("RLock em recursão de 5 níveis:", recursive(5))

# Semaphore: no máximo N ao mesmo tempo (ex.: limitar conexões)
semaphore = threading.Semaphore(3)
inside, peak = 0, 0
guard = threading.Lock()


def limited(i):
    global inside, peak
    with semaphore:
        with guard:
            inside += 1
            peak = max(peak, inside)
        time.sleep(0.05)
        with guard:
            inside -= 1


threads = [threading.Thread(target=limited, args=(i,)) for i in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("10 threads, Semaphore(3): pico de simultâneas =", peak)

# Event: um sinal que várias threads esperam
ready = threading.Event()
log = []


def waiter(i):
    ready.wait()
    log.append(i)


waiters = [threading.Thread(target=waiter, args=(i,)) for i in range(3)]
for t in waiters:
    t.start()
time.sleep(0.05)
print("antes do set():", log, "| set:", ready.is_set())
ready.set()
for t in waiters:
    t.join()
print("depois do set():", sorted(log))

# Condition: esperar até uma condição sobre estado compartilhado
items, cond = [], threading.Condition()


def consumer():
    with cond:
        cond.wait_for(lambda: len(items) >= 3, timeout=2)         # sempre com o PREDICADO (despertares falsos)
        return list(items)


got = []
t = threading.Thread(target=lambda: got.append(consumer()))
t.start()
for i in range(3):
    with cond:
        items.append(i)
        cond.notify_all()
    time.sleep(0.01)
t.join()
print("Condition.wait_for entregou:", got[0])

# Barrier: todos esperam todos
barrier = threading.Barrier(3)
arrivals = []


def runner(i):
    time.sleep(0.02 * i)
    barrier.wait()
    arrivals.append(time.perf_counter())


ts = [threading.Thread(target=runner, args=(i,)) for i in range(3)]
for t in ts:
    t.start()
for t in ts:
    t.join()
print(f"Barrier: as 3 saíram juntas (dispersão {1e3 * (max(arrivals) - min(arrivals)):.1f} ms, apesar de chegarem com 40 ms de diferença)")

# Custos
l = threading.Lock()


def acquire_release():
    l.acquire()
    l.release()


def with_lock():
    with l:
        pass


r = threading.RLock()


def with_rlock():
    with r:
        pass


print("custo por operação (ns):")
for label, fn in [("acquire + release", acquire_release), ("with Lock", with_lock), ("with RLock", with_rlock)]:
    print(f"  {label:<18}{min(timeit.repeat(fn, number=500_000, repeat=3)) / 500_000 * 1e9:6.0f}")
