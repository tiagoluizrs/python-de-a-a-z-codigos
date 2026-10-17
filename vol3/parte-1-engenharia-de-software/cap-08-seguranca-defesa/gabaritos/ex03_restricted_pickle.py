"""Gabarito do exercício 3."""
import io
import pickle


class _Unpickler(pickle.Unpickler):
    def __init__(self, file, allowed):
        super().__init__(file)
        self._allowed = allowed

    def find_class(self, module, name):
        if (module, name) in self._allowed:
            return super().find_class(module, name)
        raise pickle.UnpicklingError(f"proibido: {module}.{name}")


def restricted_loads(data, allowed=frozenset()):
    return _Unpickler(io.BytesIO(data), frozenset(allowed)).load()
