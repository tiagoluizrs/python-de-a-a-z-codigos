"""Conjuntos: criação, álgebra, comparações."""
print(type({}), type(set()), type({1, 2}))
print(set("banana") == {"a", "b", "n"}, set([3, 1, 3, 2]))
print({x % 3 for x in range(10)})

a, b = {1, 2, 3, 4}, {3, 4, 5}
print(a | b, a & b, a - b, a ^ b)
print(a.union(b), a.intersection([3, 9]), a.difference([1]))
print({1, 2} <= a, {1, 2} < a, a >= {1}, a.issubset({1, 2, 3, 4, 5}))
print(a.isdisjoint({8, 9}), a.isdisjoint(b))

s = {1, 2}
s.add(3)
s.add(3)
s.discard(99)                        # não falha
try:
    s.remove(99)
except KeyError as error:
    print("KeyError:", error)
print(s)
s |= {7}
s &= {2, 3, 7}
s -= {7}
s ^= {9}
print(s)
s.update([10, 11])
s.intersection_update({2, 10})
print(s)

# Métodos aceitam qualquer iterável; operadores exigem set
print({1, 2}.union([3], (4, 5), range(6, 8)))
try:
    {1, 2} | [3]
except TypeError as error:
    print("TypeError:", error)

# frozenset: imutável e hasheável
fs = frozenset({1, 2})
print(fs | {3}, type(fs | {3}), type({3} | fs))
print(hash(fs) == hash(frozenset({2, 1})))
print({frozenset({1, 2}): 1}[frozenset({2, 1})])
try:
    {[1]}
except TypeError as error:
    print("TypeError:", error)
try:
    {{1}}
except TypeError as error:
    print("TypeError:", error)
print(set() == frozenset(), {1} == frozenset({1}))
