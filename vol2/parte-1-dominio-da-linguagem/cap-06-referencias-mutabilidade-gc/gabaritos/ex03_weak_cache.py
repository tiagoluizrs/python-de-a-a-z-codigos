"""Gabarito do exercício 3."""
from weakref import WeakValueDictionary


class Document:
    def __init__(self, name: str) -> None:
        self.name = name


class WeakCache:
    def __init__(self) -> None:
        # Os valores são fracos: o cache NÃO mantém os documentos vivos
        self._data: WeakValueDictionary[str, Document] = WeakValueDictionary()
        self.created = 0

    def get(self, name: str) -> Document:
        doc = self._data.get(name)       # None se nunca existiu ou já morreu
        if doc is None:
            doc = Document(name)
            self._data[name] = doc
            self.created += 1
        return doc

    def __len__(self) -> int:
        return len(self._data)
