"""Gabarito do exercício 4."""
import sqlite3
from dataclasses import dataclass


@dataclass
class Item:
    id: int
    name: str
    qty: int


class Session:
    def __init__(self, conn):
        self.conn = conn
        self._reset()

    def _reset(self):
        self._identity = {}                                  # id -> Item (carregados e novos; os apagados continuam aqui até o commit)
        self._snapshots = {}                                 # id -> (name, qty) dos carregados
        self._new = {}                                       # id -> Item a inserir
        self._deleted = set()                                # ids a apagar

    def get(self, item_id):
        if item_id in self._deleted:
            raise KeyError(f"item inexistente: {item_id}")
        if item_id in self._identity:
            return self._identity[item_id]
        row = self.conn.execute("SELECT id, name, qty FROM items WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise KeyError(f"item inexistente: {item_id}")
        item = Item(*row)
        self._identity[item_id] = item
        self._snapshots[item_id] = (item.name, item.qty)
        return item

    def add(self, item):
        if item.id in self._identity or self.conn.execute("SELECT 1 FROM items WHERE id = ?", (item.id,)).fetchone() is not None:
            raise ValueError(f"item já existe: {item.id}")
        self._identity[item.id] = item
        self._new[item.id] = item

    def delete(self, item):
        if self._identity.get(item.id) is not item:
            raise ValueError("item não gerenciado")
        self._deleted.add(item.id)

    def dirty(self):
        return sorted(
            item_id for item_id, snapshot in self._snapshots.items()
            if item_id not in self._deleted and (self._identity[item_id].name, self._identity[item_id].qty) != snapshot
        )

    def commit(self):
        for item_id, item in self._new.items():
            if item_id not in self._deleted:
                self.conn.execute("INSERT INTO items (id, name, qty) VALUES (?, ?, ?)", (item.id, item.name, item.qty))
        for item_id in self.dirty():
            item = self._identity[item_id]
            self.conn.execute("UPDATE items SET name = ?, qty = ? WHERE id = ?", (item.name, item.qty, item_id))
        for item_id in sorted(self._deleted - self._new.keys()):
            self.conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.conn.commit()
        for item_id in self._deleted:
            del self._identity[item_id]
            self._snapshots.pop(item_id, None)
        for item_id, item in self._identity.items():
            self._snapshots[item_id] = (item.name, item.qty)
        self._new, self._deleted = {}, set()

    def rollback(self):
        self.conn.rollback()
        self._reset()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None or self._new or self._deleted or self.dirty():
            self.rollback()
        return False
