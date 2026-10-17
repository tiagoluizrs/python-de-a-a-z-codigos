"""Gabarito do exercício 3."""
from contextlib import ExitStack


def read_all(paths, opener=open):
    with ExitStack() as stack:
        # se opener falhar no meio, o ExitStack fecha os anteriores
        handles = [stack.enter_context(opener(path)) for path in paths]
        return [handle.read() for handle in handles]
