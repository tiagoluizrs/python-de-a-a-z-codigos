"""collections, heapq, bisect, deque, graphlib em poucas linhas."""
import bisect
import heapq
from collections import ChainMap, Counter, defaultdict, deque, namedtuple
from graphlib import TopologicalSorter

words = "to be or not to be that is the question".split()
print(Counter(words).most_common(2))

groups = defaultdict(list)
for w in words:
    groups[len(w)].append(w)
print(dict(groups))

last3 = deque(maxlen=3)
for n in range(6):
    last3.append(n)
print(last3)

Point = namedtuple("Point", "x y")
print(Point(1, 2), Point(1, 2)._asdict())

defaults = {"color": "red", "size": 1}
cli = {"size": 9}
cfg = ChainMap(cli, defaults)
print(cfg["size"], cfg["color"])

heap = [5, 1, 4, 2]
heapq.heapify(heap)
print(heapq.heappop(heap), heapq.nsmallest(2, [9, 3, 7, 1]))

# bisect: em qual faixa cai a nota 75?
print("ABCD"[bisect.bisect([60, 70, 80], 75)])

deps = {"app": {"lib", "log"}, "lib": {"core"}, "log": {"core"}}
print(list(TopologicalSorter(deps).static_order()))
