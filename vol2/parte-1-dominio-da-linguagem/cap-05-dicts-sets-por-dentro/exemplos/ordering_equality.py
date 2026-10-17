"""Ordem de inserção, igualdade e métodos de dict que dependem dela."""
from collections import OrderedDict

print({1: 2, 3: 4} == {3: 4, 1: 2})                       # True
a = OrderedDict([(1, 2), (3, 4)])
b = OrderedDict([(3, 4), (1, 2)])
print(a == b, a == {3: 4, 1: 2})                           # False True

d = {1: "a", 2: "b", 3: "c"}
print(d.popitem(), d)                                       # LIFO

od = OrderedDict.fromkeys("abc")
od.move_to_end("a")
print(list(od))                                             # ['b', 'c', 'a']
od.move_to_end("c", last=False)
print(list(od))                                             # ['c', 'b', 'a']


class Doubling(dict):
    def __missing__(self, key):
        return key * 2


print(Doubling()[21], Doubling().get(21))                   # 42 None
print({1: "a", 1.0: "b", True: "c"})                        # {1: 'c'}
