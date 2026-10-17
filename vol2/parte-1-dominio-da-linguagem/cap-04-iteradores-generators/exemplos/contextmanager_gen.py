"""contextmanager: um gerador com um unico yield."""
from contextlib import contextmanager
import time


@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield start
    finally:
        print(f"{label}: terminou")


with timer("tarefa") as t0:
    print("dentro", type(t0).__name__)

try:
    with timer("com erro"):
        raise ValueError("falhou")
except ValueError as exc:
    print("propagou", exc)


@contextmanager
def no_yield():
    if False:
        yield


try:
    with no_yield():
        pass
except RuntimeError as exc:
    print("RuntimeError:", exc)
