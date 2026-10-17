"""Gabarito do exercício 2."""
import copy
from contextlib import contextmanager


class Inventory:
    def __init__(self):
        self._stock, self._labels = {}, {}
        self.commits = self.rollbacks = 0

    @staticmethod
    def _check(qty):
        if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
            raise ValueError("quantidade inválida")

    def add(self, item, qty):
        self._check(qty)
        self._stock[item] = self._stock.get(item, 0) + qty

    def remove(self, item, qty):
        self._check(qty)
        if self._stock.get(item, 0) < qty:
            raise ValueError(f"estoque insuficiente: {item}")
        self._stock[item] -= qty
        if self._stock[item] == 0:
            del self._stock[item]
            self._labels.pop(item, None)

    def label(self, item, text):
        if item not in self._stock:
            raise LookupError(item)
        self._labels.setdefault(item, []).append(text)

    def quantity(self, item):
        return self._stock.get(item, 0)

    def labels_of(self, item):
        return list(self._labels.get(item, []))

    @contextmanager
    def transaction(self, dry_run=False):
        snapshot = copy.deepcopy((self._stock, self._labels))
        try:
            yield self
        except BaseException:
            self._stock, self._labels = snapshot
            self.rollbacks += 1
            raise
        if dry_run:
            self._stock, self._labels = snapshot
            self.rollbacks += 1
        else:
            self.commits += 1
