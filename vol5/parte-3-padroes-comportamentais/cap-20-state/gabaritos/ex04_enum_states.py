"""Gabarito do exercício 4."""
from enum import Enum

_SECONDS = {"red": 30, "green": 25, "yellow": 5}
_NEXT = {"red": "green", "green": "yellow", "yellow": "red"}


class Light(Enum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"

    @property
    def seconds(self):
        return _SECONDS[self.value]

    def next(self):
        return Light(_NEXT[self.value])


class TrafficLight:
    def __init__(self, initial=Light.RED):
        self._state, self._elapsed = initial, 0

    @property
    def state(self):
        return self._state

    @property
    def elapsed(self):
        return self._elapsed

    @property
    def remaining(self):
        return self._state.seconds - self._elapsed

    def tick(self, seconds):
        if seconds < 0:
            raise ValueError("tempo negativo")
        entered = []
        self._elapsed += seconds
        while self._elapsed >= self._state.seconds:
            self._elapsed -= self._state.seconds
            self._state = self._state.next()
            entered.append(self._state)
        return entered

    @staticmethod
    def cycle_length():
        return sum(light.seconds for light in Light)


def door(state, event):
    if state not in ("closed", "open", "locked"):
        raise ValueError(f"estado desconhecido: {state}")
    if event not in ("open", "close", "lock", "unlock"):
        raise ValueError(f"evento desconhecido: {event}")
    match (state, event):
        case ("closed", "open"):
            return "open"
        case ("closed", "lock"):
            return "locked"
        case ("open", "close"):
            return "closed"
        case ("locked", "unlock"):
            return "closed"
        case _:
            raise ValueError(f"{event} não permitido em {state}")
