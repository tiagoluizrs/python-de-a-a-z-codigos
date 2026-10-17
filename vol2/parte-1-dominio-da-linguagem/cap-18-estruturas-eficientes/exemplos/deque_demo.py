"""deque: fila de duas pontas, janela deslizante e o custo do meio."""
import timeit
from collections import deque

d = deque([1, 2, 3], maxlen=3)
d.append(4)                                    # descarta o 1 (maxlen) pela ponta oposta
d.appendleft(0)                                # descarta o 4
print(d, d.maxlen)

r = deque(range(5))
r.rotate(2)
print(r)
r.rotate(-1)
print(r)

# Operações das pontas: O(1). Do meio: O(n)
try:
    deque(range(3)).insert(1, 9)               # existe, mas é O(n)
    print("insert existe (O(n))")
except IndexError as error:
    print("IndexError:", error)

# extendleft inverte a ordem (cada item entra pela esquerda)
x = deque([1])
x.extendleft([2, 3, 4])
print(x)

# Janela deslizante: média móvel
window = deque(maxlen=3)
averages = []
for value in [10, 20, 30, 40, 50]:
    window.append(value)
    averages.append(sum(window) / len(window))
print(averages)

# Busca em largura (BFS) usa a fila FIFO
graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
queue, seen, order = deque(["a"]), {"a"}, []
while queue:
    node = queue.popleft()
    order.append(node)
    for nxt in graph[node]:
        if nxt not in seen:
            seen.add(nxt)
            queue.append(nxt)
print(order)

# Medidas: lista x deque (100 mil itens)
base = list(range(100_000))
ns = dict(L=list(base), D=deque(base))
print("operação                          ns")
for label, statement, number in [
    ("lista: pop(0) + append", "L.pop(0); L.append(0)", 2000),
    ("deque: popleft + append", "D.popleft(); D.append(0)", 200_000),
    ("lista: insert(0) + pop(0)", "L.insert(0, 0); L.pop(0)", 2000),
    ("deque: appendleft + popleft", "D.appendleft(0); D.popleft()", 200_000),
    ("lista: L[50000]", "L[50000]", 200_000),
    ("deque: D[50000]", "D[50000]", 20_000),
    ("deque: D[0]", "D[0]", 1_000_000),
]:
    seconds = min(timeit.repeat(statement, globals=ns, number=number, repeat=3)) / number
    print(f"  {label:<30}{seconds * 1e9:10.1f}")
