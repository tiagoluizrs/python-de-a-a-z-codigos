"""Tabela de decisão com medidas: qual estrutura para qual operação."""
import bisect
import heapq
import timeit
from collections import deque

N = 100_000
L = list(range(N))
S = set(L)
D = dict.fromkeys(L)
Q = deque(L)
ns = dict(L=L, S=S, D=D, Q=Q, bisect=bisect, heapq=heapq, N=N)
print("busca de um item no fim (ns):")
for label, statement in [("lista (in)", "N - 1 in L"), ("set (in)", "N - 1 in S"), ("dict (in)", "N - 1 in D"),
                         ("bisect (lista ordenada)", "bisect.bisect_left(L, N - 1)")]:
    seconds = min(timeit.repeat(statement, globals=ns, number=300, repeat=3)) / 300
    print(f"  {label:<28}{seconds * 1e9:12.0f}")

heap = list(range(1000))
heapq.heapify(heap)
ns["heap"] = heap
print("heap (1000 itens) push+pop (ns):")
seconds = min(timeit.repeat("heapq.heappush(heap, 500); heapq.heappop(heap)", globals=ns, number=200_000, repeat=3)) / 200_000
print(f"  heappush+heappop{seconds * 1e9:10.0f}")
