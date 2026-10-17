"""Gabarito do exercício 6."""
import queue
import threading


def run_workers(tasks, handler, concurrency=4, max_attempts=3, queue_size=10):
    if concurrency < 1 or max_attempts < 1:
        raise ValueError("concurrency e max_attempts devem ser >= 1")
    if not tasks:
        return {"ok": [], "failed": [], "attempts": {}}
    inbox: queue.Queue = queue.Queue(maxsize=queue_size)
    retries: queue.Queue = queue.Queue()                    # sem limite: reenviar nunca bloqueia um worker
    lock = threading.Lock()
    results: dict[int, object] = {}
    failures: dict[int, tuple] = {}
    attempts: dict[int, int] = {}
    pending = {"count": len(tasks)}
    finished = threading.Event()

    def worker():
        while True:
            try:
                job = retries.get_nowait()
            except queue.Empty:
                try:
                    job = inbox.get(timeout=0.02)
                except queue.Empty:
                    if finished.is_set():
                        return
                    continue
            if job is None:
                return
            index, item, attempt = job
            try:
                value = handler(item)
            except Exception as error:
                with lock:
                    attempts[index] = attempt
                if attempt < max_attempts:
                    retries.put((index, item, attempt + 1))
                    continue
                with lock:
                    failures[index] = (item, error)
                    pending["count"] -= 1
            else:
                with lock:
                    attempts[index] = attempt
                    results[index] = value
                    pending["count"] -= 1
            with lock:
                if pending["count"] == 0:
                    finished.set()

    threads = [threading.Thread(target=worker) for _ in range(concurrency)]
    for t in threads:
        t.start()
    for index, item in enumerate(tasks):
        inbox.put((index, item, 1))                           # bloqueia quando a fila está cheia (contrapressão)
    for t in threads:
        t.join()
    return {
        "ok": [results[i] for i in sorted(results)],
        "failed": [failures[i] for i in sorted(failures)],
        "attempts": dict(sorted(attempts.items())),
    }
