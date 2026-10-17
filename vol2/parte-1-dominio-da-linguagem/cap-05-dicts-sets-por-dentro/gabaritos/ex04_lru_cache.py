"""Gabarito do exercício 4."""


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._data = {}                       # a ordem do dict é a ordem de uso

    def get(self, key, default=None):
        if key not in self._data:
            return default
        value = self._data.pop(key)           # remove e reinsere: vai para o fim
        self._data[key] = value
        return value

    def put(self, key, value):
        self._data.pop(key, None)
        self._data[key] = value
        if len(self._data) > self.capacity:
            oldest = next(iter(self._data))   # o primeiro é o menos recente
            del self._data[oldest]

    def __len__(self):
        return len(self._data)

    def keys(self):
        return list(self._data)
