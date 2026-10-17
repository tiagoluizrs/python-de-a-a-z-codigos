"""Threads em tarefas de CPU: build com GIL contra build sem GIL."""
import builds

PAYLOAD = """
import threading, time
def cpu(n):
    t = 0
    for i in range(n): t += i * i
    return t
TASKS = 16
seqs = []
for _ in range(3):
    t = time.perf_counter()
    for _ in range(TASKS): cpu(400_000)
    seqs.append(time.perf_counter() - t)
seq = min(seqs)
row = [f"{seq:.3f}"]
for workers in (1, 2, 4, 8, 16):
    threads = [threading.Thread(target=lambda: [cpu(400_000) for _ in range(TASKS // workers)]) for _ in range(workers)]
    t = time.perf_counter()
    for x in threads: x.start()
    for x in threads: x.join()
    row.append(f"{time.perf_counter() - t:.3f}")
print(" ".join(row))
"""

if __name__ == "__main__":
    print("16 tarefas de CPU divididas em N threads (mesma carga total):")
    print(f"{'build':<18}{'sequencial':>11}" + "".join(f"{n:>9} thr" for n in (1, 2, 4, 8, 16)))
    for label, python in builds.builds():
        if not python:
            continue
        values = [float(v) for v in builds.run_code(python, PAYLOAD).split()]
        seq, rest = values[0], values[1:]
        print(f"{label:<18}{seq:>10.2f}s" + "".join(f"{v:>8.2f}s" for v in rest))
        print(f"{'  ganho':<18}{'':>11}" + "".join(f"{seq / v:>8.1f}x" for v in rest))
