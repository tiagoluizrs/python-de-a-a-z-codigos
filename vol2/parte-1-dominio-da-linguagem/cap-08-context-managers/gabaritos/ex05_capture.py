"""Gabarito do exercício 5."""
import io
from contextlib import contextmanager, redirect_stdout


class _Captured:
    def __init__(self, buffer):
        self._buffer = buffer

    def lines(self):
        return self._buffer.getvalue().splitlines()


@contextmanager
def capture_prints():
    buffer = io.StringIO()
    with redirect_stdout(buffer):       # restaura sys.stdout mesmo com exceção
        yield _Captured(buffer)
