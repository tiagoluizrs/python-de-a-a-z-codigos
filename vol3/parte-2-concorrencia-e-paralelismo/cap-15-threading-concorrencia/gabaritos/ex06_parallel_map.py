"""Gabarito do exercício 6."""
import queue
import threading


def threaded_map(func, items, workers=4, stop_on_error=False):
    if workers < 1:
        raise ValueError("workers >= 1")
    items = list(items)
    if not items:
        return []
    results = [None] * len(items)
    errors = {}
    stop = threading.Event()
    jobs = queue.Queue()
    for index in range(len(items)):
        jobs.put(index)

    def run():
        while True:
            try:
                index = jobs.get_nowait()
            except queue.Empty:
                return
            if stop_on_error and stop.is_set():
                continue
            try:
                results[index] = func(items[index])
            except BaseException as error:         # noqa: BLE001
                errors[index] = error
                stop.set()

    threads = [threading.Thread(target=run) for _ in range(min(workers, len(items)))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    if errors:
        raise errors[min(errors)]
    return results
