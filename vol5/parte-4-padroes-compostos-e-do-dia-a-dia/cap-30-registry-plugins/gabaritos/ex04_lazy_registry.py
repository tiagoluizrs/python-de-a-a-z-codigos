"""Gabarito do exercício 4."""
import importlib
import threading


class LazyRegistry:
    def __init__(self):
        self._targets, self._loaded = {}, {}
        self._lock = threading.RLock()

    def register(self, name, target, *, replace=False):
        with self._lock:
            if name in self._targets and not replace:
                raise ValueError(f"já registrado: {name}")
            if isinstance(target, str):
                module, sep, attribute = target.partition(":")
                if sep != ":" or ":" in attribute or not module.strip() or not attribute.strip() or module != module.strip() or attribute != attribute.strip():
                    raise ValueError(f"caminho inválido: {target!r}")
            self._targets[name] = target
            self._loaded.pop(name, None)
            if not isinstance(target, str):
                self._loaded[name] = target

    def _load(self, name):
        target = self._targets[name]
        module_name, _, attribute = target.partition(":")
        try:
            obj = importlib.import_module(module_name)
            for part in attribute.split("."):
                obj = getattr(obj, part)
        except (ImportError, AttributeError) as error:
            raise LookupError(f"não pôde ser carregado: {name!r} ({type(error).__name__}: {error})") from error
        return obj

    def get(self, name):
        with self._lock:
            if name not in self._targets:
                available = ", ".join(sorted(self._targets)) or "nenhum"
                raise KeyError(f"desconhecido: {name!r}; disponíveis: {available}")
            if name not in self._loaded:
                self._loaded[name] = self._load(name)
            return self._loaded[name]

    def names(self):
        with self._lock:
            return sorted(self._targets)

    def loaded(self):
        with self._lock:
            return sorted(self._loaded)

    def is_loaded(self, name):
        return name in self._loaded

    def preload(self, *names):
        with self._lock:
            before = set(self._loaded)
            for name in names or self.names():
                self.get(name)
            return sorted(set(self._loaded) - before)

    def __contains__(self, name):
        return name in self._targets

    def __len__(self):
        return len(self._targets)
