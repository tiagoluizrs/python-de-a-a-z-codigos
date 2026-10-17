"""Gabarito do exercício 5."""
import threading
from concurrent import interpreters

_CODE = """
total = 0
while (item := jobs.get()) is not None:
    total += item
results.put(total)
"""


def sum_in_interpreter(numbers):
    interp = interpreters.create()
    try:
        jobs = interpreters.create_queue()
        results = interpreters.create_queue()
        interp.prepare_main(jobs=jobs, results=results)
        worker = threading.Thread(target=interp.exec, args=(_CODE,))
        worker.start()
        for number in numbers:
            jobs.put(number)
        jobs.put(None)
        total = results.get(timeout=30)
        worker.join()
        return total
    finally:
        interp.close()
