"""Filas: a forma segura de passar dados entre threads."""
import queue
import threading
import time

# Produtor/consumidor com sentinela
q = queue.Queue(maxsize=5)                     # limite: o produtor ESPERA quando a fila enche (contrapressão)
SENTINEL = object()
processed = []


def producer(n):
    for i in range(n):
        q.put(i)
    q.put(SENTINEL)


def consumer():
    while (item := q.get()) is not SENTINEL:
        processed.append(item * item)
        q.task_done()
    q.task_done()


p, c = threading.Thread(target=producer, args=(20,)), threading.Thread(target=consumer)
p.start()
c.start()
p.join()
q.join()                                       # espera TODOS os itens serem marcados com task_done()
c.join()
print("processados:", processed[:6], "...", len(processed), "itens")

# Vários consumidores: uma sentinela para CADA um
work = queue.Queue()
results = queue.Queue()


def pool_worker():
    while (job := work.get()) is not None:
        results.put((threading.current_thread().name, job * 2))


workers = [threading.Thread(target=pool_worker, name=f"w{i}") for i in range(3)]
for w in workers:
    w.start()
for job in range(9):
    work.put(job)
for _ in workers:
    work.put(None)
for w in workers:
    w.join()
done = [results.get() for _ in range(9)]
print("9 trabalhos em 3 workers; soma dos resultados:", sum(v for _, v in done), "| workers que participaram:", sorted({n for n, _ in done}))

# Tipos de fila
pq = queue.PriorityQueue()
for priority, name in [(3, "baixa"), (1, "alta"), (2, "média")]:
    pq.put((priority, name))
lifo = queue.LifoQueue()
for x in (1, 2, 3):
    lifo.put(x)
print("PriorityQueue:", [pq.get()[1] for _ in range(3)], "| LifoQueue:", [lifo.get() for _ in range(3)])

# Timeouts e filas vazias/cheias
try:
    queue.Queue().get(timeout=0.05)
except queue.Empty:
    print("get(timeout) em fila vazia -> queue.Empty")
full = queue.Queue(maxsize=1)
full.put(1)
try:
    full.put(2, block=False)
except queue.Full:
    print("put(block=False) em fila cheia -> queue.Full")

# Queue.shutdown() (3.13+): encerrar sem sentinelas
sq = queue.Queue()
sq.put("a")
sq.shutdown()
print("depois de shutdown(): get() ->", sq.get(), "| de novo ->", end=" ")
try:
    sq.get()
except queue.ShutDown:
    print("queue.ShutDown")

# Custo
import collections
import timeit

plain, dq = queue.Queue(), collections.deque()


def queue_op():
    plain.put(1)
    plain.get()


def deque_op():
    dq.append(1)
    dq.popleft()


print("custo (ns): Queue put+get", round(min(timeit.repeat(queue_op, number=200_000, repeat=3)) / 200_000 * 1e9),
      "| deque append+popleft", round(min(timeit.repeat(deque_op, number=500_000, repeat=3)) / 500_000 * 1e9),
      "(a deque é atômica, mas não bloqueia nem tem limite)")
