"""Gabarito do exercício 4."""
from typing import Protocol, runtime_checkable


@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None: ...


def close_all(items):
    closed = 0
    first_error = None
    for item in items:
        if not isinstance(item, SupportsClose):
            continue
        try:
            item.close()
            closed += 1
        except Exception as error:                  # as demais continuam sendo fechadas
            if first_error is None:
                first_error = error
    if first_error is not None:
        raise first_error
    return closed
