"""Subinterpretadores em threads: cada um tem o SEU GIL (build com GIL)... e no build sem GIL?"""
import builds

PAYLOAD = """
import threading, time
from concurrent import interpreters
CODE = "s = 0\\nfor k in range(400000): s += k * k"
def run():
    interp = interpreters.create(); interp.exec(CODE); interp.close()
def plain():
    exec(CODE)
def timed(target, n):
    ts = [threading.Thread(target=target) for _ in range(n)]
    t = time.perf_counter()
    for x in ts: x.start()
    for x in ts: x.join()
    return (time.perf_counter() - t) * 1e3
out = []
for n in (1, 4, 8, 16):
    out.append(timed(run, n))
for n in (1, 4, 8, 16):
    out.append(timed(plain, n))
print(" ".join(f"{v:.0f}" for v in out))
"""

if __name__ == "__main__":
    print("N threads, cada uma com uma tarefa de CPU (~50 ms). Tempo total em ms:")
    print(f"{'build / execução':<34}" + "".join(f"{n:>8}" for n in (1, 4, 8, 16)))
    for label, python in builds.builds():
        if not python:
            continue
        values = [float(v) for v in builds.run_code(python, PAYLOAD).split()]
        print(f"{label + ' / subinterpretadores':<34}" + "".join(f"{v:>8.0f}" for v in values[:4]))
        print(f"{label + ' / threads comuns':<34}" + "".join(f"{v:>8.0f}" for v in values[4:]))
    print("(ideal: o tempo ficar parado em ~50 ms enquanto N cresce)")
