"""Free-threading não é de graça: estado compartilhado disputado fica MAIS LENTO."""
import builds

PAYLOAD = """
import threading, time
N = 100_000
def run(target, threads=8):
    ts = [threading.Thread(target=target, args=(k,)) for k in range(threads)]
    t = time.perf_counter()
    for x in ts: x.start()
    for x in ts: x.join()
    return time.perf_counter() - t

shared = {}
def write_shared(k):
    for i in range(N): shared[(k, i)] = i

results = []
def write_local(k):
    local = {}
    for i in range(N): local[(k, i)] = i
    results.append(local)               # UMA operação compartilhada por thread

shared_list = []
def append_shared(k):
    for i in range(N): shared_list.append(i)

print(f"{run(write_shared):.3f} {run(write_local):.3f} {run(append_shared):.3f}")
"""

if __name__ == "__main__":
    print("8 threads, 100.000 escritas cada:")
    print(f"{'build':<18}{'dict compartilhado':>20}{'dict por thread':>18}{'list.append compart.':>23}")
    for label, python in builds.builds():
        if python:
            a, b, c = builds.run_code(python, PAYLOAD).split()
            print(f"{label:<18}{a + ' s':>20}{b + ' s':>18}{c + ' s':>23}")
    print("moral: sem GIL, threads escrevendo no MESMO objeto disputam a trava interna dele; dê a cada thread o seu estado e junte no fim.")
