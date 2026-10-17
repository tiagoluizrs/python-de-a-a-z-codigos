"""Custo das operações de lista: meça, não adivinhe."""
import timeit
from collections import deque


def per_call(stmt, namespace, number):
    return min(timeit.repeat(stmt, number=number, repeat=3, globals=namespace)) / number


for n in (1_000, 100_000):
    items = list(range(n))
    queue = deque(items)
    ns = {"items": items, "queue": queue}
    print(f"--- n = {n:,}")
    print(f"append + pop()       {per_call('items.append(1); items.pop()', ns, 100_000) * 1e9:>10,.0f} ns")
    print(f"insert(0) + pop(0)   {per_call('items.insert(0, 1); items.pop(0)', ns, 200) * 1e9:>10,.0f} ns")
    print(f"deque left ops       {per_call('queue.appendleft(1); queue.popleft()', ns, 100_000) * 1e9:>10,.0f} ns")
    print(f"items[n // 2]        {per_call('items[len(items) // 2]', ns, 100_000) * 1e9:>10,.0f} ns")
    print(f"-1 in items (miss)   {per_call('-1 in items', ns, 100) * 1e9:>10,.0f} ns")
    print(f"items[:] (copy)      {per_call('items[:]', ns, 200) * 1e9:>10,.0f} ns")

# Concatenar com + em laço é quadrático
slow = timeit.timeit("l = []\nfor i in range(2000): l = l + [i]", number=20) / 20
fast = timeit.timeit("l = []\nfor i in range(2000): l.append(i)", number=20) / 20
print(f"\nl = l + [i]: {slow * 1e6:,.0f} us   l.append(i): {fast * 1e6:,.0f} us   ({slow / fast:.0f}x)")
