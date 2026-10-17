"""Gabarito do exercício 4."""


class Plane:
    def __init__(self, name):
        self.name, self.messages = name, []

    def notify(self, message):
        self.messages.append(message)


class Tower:
    def __init__(self):
        self._runway = None
        self._queue = []                      # lista de (avião, emergência)
        self._announced = {}                  # avião (id) -> última posição avisada

    def _positions(self):
        return {id(plane): i for i, (plane, _) in enumerate(self._queue, start=1)}

    def _sync_positions(self):
        for plane, _ in self._queue:
            position = self._positions()[id(plane)]
            if self._announced.get(id(plane)) != position:
                self._announced[id(plane)] = position
                plane.notify(f"na fila: posição {position}")

    def request_landing(self, plane, emergency=False):
        if plane is self._runway or any(p is plane for p, _ in self._queue):
            raise ValueError(f"{plane.name} já está no sistema")
        if self._runway is None:
            self._runway = plane
            plane.notify("pouso autorizado")
            return 0
        if emergency:
            index = sum(1 for _, e in self._queue if e)
            self._queue.insert(index, (plane, True))
        else:
            self._queue.append((plane, False))
        self._sync_positions()
        return self._positions()[id(plane)]

    def landed(self, plane):
        if plane is not self._runway:
            raise ValueError(f"{plane.name} não está na pista")
        self._runway = None
        if not self._queue:
            return None
        nxt, _ = self._queue.pop(0)
        self._announced.pop(id(nxt), None)
        self._runway = nxt
        nxt.notify("pouso autorizado")
        self._sync_positions()
        return nxt

    def cancel(self, plane):
        if plane is self._runway:
            raise ValueError("avião na pista não pode cancelar")
        for i, (p, _) in enumerate(self._queue):
            if p is plane:
                del self._queue[i]
                self._announced.pop(id(plane), None)
                self._sync_positions()
                return
        raise LookupError(f"{plane.name} não está na fila")

    @property
    def runway(self):
        return self._runway

    def waiting(self):
        return [p.name for p, _ in self._queue]

    def __len__(self):
        return len(self._queue) + (1 if self._runway is not None else 0)
