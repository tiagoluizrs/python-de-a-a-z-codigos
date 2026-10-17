"""Gabarito do exercício 5."""
import logging
import time


class DuplicateFilter(logging.Filter):
    def __init__(self, window=5.0, clock=time.monotonic):
        super().__init__()
        self.window = window
        self.clock = clock
        self._state = {}                      # chave -> [início da janela, suprimidas]

    def filter(self, record):
        key = (record.name, record.levelno, record.getMessage())
        now = self.clock()
        state = self._state.get(key)
        if state is None:
            self._state[key] = [now, 0]
            return True
        if now - state[0] < self.window:
            state[1] += 1
            return False
        suppressed = state[1]
        if suppressed:
            record.msg = f"{record.getMessage()} (+{suppressed} repetidas)"
            record.args = ()
        self._state[key] = [now, 0]
        return True
