"""heapq: filas de prioridade, top-k e mesclagem."""
import heapq
import random
import timeit

heap = []
for value in [5, 1, 4, 2]:
    heapq.heappush(heap, value)
print(heap, "<- é um heap, NÃO uma lista ordenada")
print(heapq.heappop(heap), heapq.heappop(heap), heap)

# heapify: O(n) no lugar
data = [9, 3, 7, 1, 8]
heapq.heapify(data)
print(data[0], sorted(data))

# Os k maiores / menores
print(heapq.nlargest(2, [9, 3, 7, 1]), heapq.nsmallest(2, [9, 3, 7, 1]))
words = ["pera", "uva", "abacaxi", "kiwi"]
print(heapq.nlargest(2, words, key=len))

# Mesclar fluxos JÁ ordenados, de forma preguiçosa
print(list(heapq.merge([1, 4, 7], [2, 5, 8], [3, 6, 9])))

# Max-heap (3.14+): funções *_max
mh = [3, 9, 1]
heapq.heapify_max(mh)
print(heapq.heappop_max(mh), heapq.heappop_max(mh))

# Fila de prioridade: itens iguais na prioridade exigem desempate
tasks = []
try:
    heapq.heappush(tasks, (1, {"name": "a"}))
    heapq.heappush(tasks, (1, {"name": "b"}))     # compara os dicts: TypeError
except TypeError as error:
    print("TypeError:", error)

import itertools

counter = itertools.count()
tasks = []
for priority, name in [(2, "b"), (1, "a"), (2, "c"), (1, "d")]:
    heapq.heappush(tasks, (priority, next(counter), {"name": name}))   # contador estável
print([heapq.heappop(tasks)[2]["name"] for _ in range(4)])

# Dijkstra: o uso clássico
graph = {"A": {"B": 7, "C": 9, "F": 14}, "B": {"A": 7, "C": 10, "D": 15}, "C": {"A": 9, "B": 10, "D": 11, "F": 2},
         "D": {"B": 15, "C": 11, "E": 6}, "E": {"D": 6, "F": 9}, "F": {"A": 14, "C": 2, "E": 9}}


def dijkstra(graph, start):
    dist = {start: 0}
    frontier = [(0, start)]
    while frontier:
        d, node = heapq.heappop(frontier)
        if d > dist.get(node, float("inf")):
            continue                                # entrada obsoleta
        for nxt, w in graph[node].items():
            nd = d + w
            if nd < dist.get(nxt, float("inf")):
                dist[nxt] = nd
                heapq.heappush(frontier, (nd, nxt))
    return dist


print(dijkstra(graph, "A"))

# Custos (100 mil números)
rnd = [random.random() for _ in range(100_000)]
ns = dict(rnd=rnd, heapq=heapq)
print("10 maiores de 100 mil (ms):")
for label, statement in [("max(rnd)  (só o maior)", "max(rnd)"),
                         ("heapq.nlargest(10)", "heapq.nlargest(10, rnd)"),
                         ("sorted(reverse)[:10]", "sorted(rnd, reverse=True)[:10]")]:
    seconds = min(timeit.repeat(statement, globals=ns, number=20, repeat=3)) / 20
    print(f"  {label:<26}{seconds * 1e3:7.2f}")
