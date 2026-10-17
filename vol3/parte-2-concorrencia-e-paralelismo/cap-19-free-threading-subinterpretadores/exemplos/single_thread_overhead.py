"""O custo do build sem GIL para código de UMA thread."""
import builds

PAYLOAD = """
import time
def best(fn, repeat=5):
    out = []
    for _ in range(repeat):
        t = time.perf_counter(); fn(); out.append(time.perf_counter() - t)
    return min(out)
def loop():
    t = 0
    for i in range(2_000_000): t += i * i
def calls():
    def f(x): return x + 1
    for i in range(1_000_000): f(i)
def dicts():
    d = {}
    for i in range(500_000): d[i] = i
    for i in range(500_000): d[i]
def strings():
    s = []
    for i in range(300_000): s.append(str(i))
    "".join(s)
print(f"{best(loop):.3f} {best(calls):.3f} {best(dicts):.3f} {best(strings):.3f}")
"""

if __name__ == "__main__":
    rows = {}
    for label, python in builds.builds():
        if python:
            rows[label] = [float(v) for v in builds.run_code(python, PAYLOAD).split()]
    names = ["laço de CPU", "chamadas de função", "dict (escrita+leitura)", "strings"]
    print(f"{'carga (UMA thread)':<26}" + "".join(f"{label:>18}" for label in rows) + f"{'diferença':>12}")
    labels = list(rows)
    for i, name in enumerate(names):
        values = [rows[label][i] for label in labels]
        diff = (values[-1] / values[0] - 1) * 100 if len(values) == 2 else 0
        print(f"{name:<26}" + "".join(f"{v:>16.3f} s" for v in values) + f"{diff:>+11.0f}%")
