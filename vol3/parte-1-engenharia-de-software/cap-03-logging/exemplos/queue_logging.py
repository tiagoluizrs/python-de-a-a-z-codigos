"""Logging fora do caminho crítico: QueueHandler + QueueListener."""
import io
import logging
import logging.handlers
import queue
import threading
import timeit

# Um handler lento (simula disco/rede)
class Slow(logging.StreamHandler):
    def emit(self, record):
        import time
        time.sleep(0.002)
        super().emit(record)


target = Slow(io.StringIO())
logger_direct = logging.getLogger("q.direct")
logger_direct.propagate = False
logger_direct.setLevel(logging.INFO)
logger_direct.addHandler(target)

q: queue.Queue = queue.Queue()
logger_queue = logging.getLogger("q.queued")
logger_queue.propagate = False
logger_queue.setLevel(logging.INFO)
logger_queue.addHandler(logging.handlers.QueueHandler(q))

N = 50
direct = timeit.timeit(lambda: [logger_direct.info("m %d", i) for i in range(N)], number=1)
with logging.handlers.QueueListener(q, target):                  # context manager (3.14+): start/stop
    queued = timeit.timeit(lambda: [logger_queue.info("m %d", i) for i in range(N)], number=1)
print(f"{N} chamadas: direto {direct * 1e3:.1f} ms | pela fila {queued * 1e3:.1f} ms")
print("registros entregues pelo listener:", target.stream.getvalue().count("m "), "de", 2 * N)
