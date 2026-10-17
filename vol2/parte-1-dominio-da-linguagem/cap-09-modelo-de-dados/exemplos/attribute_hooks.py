"""Acesso a atributos: __getattr__ (último recurso) e __getattribute__ (sempre)."""


class Lazy:
    def __init__(self):
        self.real = "existe"

    def __getattr__(self, name):               # só é chamado se a busca normal FALHAR
        print(f"    -> __getattr__({name!r})")
        if name.startswith("_"):
            raise AttributeError(name)
        return f"<{name} calculado>"


lazy = Lazy()
print(lazy.real)
print(lazy.other)


class Tracer:
    def __getattribute__(self, name):          # chamado em TODO acesso
        print(f"    -> __getattribute__({name!r})")
        return super().__getattribute__(name)

    value = 42


tracer = Tracer()
print(tracer.value)


class DictView:
    """Acessa chaves de um dict como atributos (somente leitura)."""

    def __init__(self, data):
        object.__setattr__(self, "_data", dict(data))

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(
                f"{type(self).__name__!r} object has no attribute {name!r}") from None

    def __setattr__(self, name, value):
        raise AttributeError("somente leitura")

    def __dir__(self):
        return sorted(self._data)


view = DictView({"host": "localhost", "port": 8080})
print(view.host, view.port, dir(view))
try:
    view.user
except AttributeError as error:
    print("AttributeError:", error)
try:
    view.port = 1
except AttributeError as error:
    print("AttributeError:", error)
print(hasattr(view, "host"), hasattr(view, "nope"), getattr(view, "nope", "padrão"))
