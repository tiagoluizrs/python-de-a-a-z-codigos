"""Gabarito do exercício 2."""
import copy
import threading


class Report:
    def __init__(self, title, sections):
        self.title, self.sections = title, sections
        self._lock = threading.Lock()
        self._cache = None

    def render(self):
        if self._cache is None:
            self._cache = f"{self.title}: " + ", ".join(self.sections)
        return self._cache

    def __copy__(self):
        clone = type(self).__new__(type(self))
        clone.__dict__.update(self.__dict__)
        clone._lock = threading.Lock()
        clone._cache = None
        return clone

    def __deepcopy__(self, memo):
        clone = type(self).__new__(type(self))
        memo[id(self)] = clone
        clone.title = self.title
        clone.sections = copy.deepcopy(self.sections, memo)
        clone._lock = threading.Lock()
        clone._cache = None
        return clone

    def with_changes(self, **changes):
        for name in changes:
            if name not in ("title", "sections"):
                raise AttributeError(f"Report não tem o atributo {name!r}")
        clone = copy.copy(self)
        for name, value in changes.items():
            setattr(clone, name, value)
        return clone
