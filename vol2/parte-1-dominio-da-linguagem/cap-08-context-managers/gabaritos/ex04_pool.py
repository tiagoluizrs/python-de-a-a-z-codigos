"""Gabarito do exercício 4."""
from contextlib import ExitStack


class Pool:
    def __init__(self, factories):
        self.factories = list(factories)
        self._stack = None

    def __enter__(self):
        with ExitStack() as stack:                      # protege a aquisição
            values = [stack.enter_context(factory()) for factory in self.factories]
            self._stack = stack.pop_all()               # sucesso: assume a posse
        return values

    def __exit__(self, exc_type, exc, tb):
        # fecha em ordem inversa e repassa a exceção do corpo
        return self._stack.__exit__(exc_type, exc, tb)
