"""O interpretador adaptativo: especialização de instruções."""
import dis
import timeit


def hot(n):
    total = 0
    for i in range(n):
        total += i * 2
    return total


hot(10)
print("---- frio (como compilado)")
dis.dis(hot)
for _ in range(2000):                                 # aquece: muitas execuções com os mesmos tipos
    hot(100)
print("---- quente (adaptativo)")
dis.dis(hot, adaptive=True)


# Estabilidade de tipos: a especialização aposta que os tipos se repetem
def add(a, b):
    return a + b


def run(values, n=200_000):
    for _ in range(n):
        for a, b in values:
            add(a, b)


stable = [(1, 2)] * 4
mixed = [(1, 2), ("a", "b"), (1.5, 2.5), ([1], [2])]
for label, values in [("tipos estáveis (4 x int)", stable), ("tipos misturados (int, str, float, list)", mixed)]:
    seconds = min(timeit.repeat(lambda: run(values, 50_000), number=1, repeat=5))
    print(f"  {label:<44}{seconds * 1e3:7.1f} ms")
