"""OrderedDict (LRU), ChainMap (camadas) e namedtuple."""
from collections import ChainMap, OrderedDict, namedtuple

# OrderedDict: ordem faz parte da igualdade; move_to_end; popitem(last=False)
od = OrderedDict(a=1, b=2, c=3)
od.move_to_end("a")
print(list(od), od.popitem(last=False))
print(OrderedDict(a=1, b=2) == OrderedDict(b=2, a=1), {"a": 1, "b": 2} == {"b": 2, "a": 1})


# O padrão LRU
class LRU:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = OrderedDict()

    def get(self, key, default=None):
        if key not in self.data:
            return default
        self.data.move_to_end(key)
        return self.data[key]

    def put(self, key, value):
        self.data[key] = value
        self.data.move_to_end(key)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)


lru = LRU(2)
lru.put("a", 1)
lru.put("b", 2)
lru.get("a")
lru.put("c", 3)
print(list(lru.data))                             # b foi o menos recente

# ChainMap: camadas de configuração sem copiar
defaults = {"color": "red", "size": 1}
user = {"size": 9}
config = ChainMap(user, defaults)
print(config["size"], config["color"], config.maps)
config["theme"] = "dark"                          # escritas vão SEMPRE para a primeira camada
print(user, defaults)
child = config.new_child({"size": 100})           # escopo temporário
print(child["size"], child.parents["size"])
del child["size"]
print(child["size"])

# namedtuple
Point = namedtuple("Point", "x y", defaults=[0])
p = Point(1)
print(p, p._replace(x=5), p._asdict(), Point._fields, Point._field_defaults)
x, y = p                                          # é uma tupla: desempacota
print(x, y, p[0], isinstance(p, tuple))
