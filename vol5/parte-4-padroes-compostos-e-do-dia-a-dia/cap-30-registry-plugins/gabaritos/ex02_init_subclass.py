"""Gabarito do exercício 2."""


class Exporter:
    registry: dict = {}
    extension: str = ""

    def __init_subclass__(cls, name=None, abstract=False, **kwargs):
        super().__init_subclass__(**kwargs)                  # primeiro: se houver um argumento desconhecido, falha ANTES de registrar
        if abstract:
            return
        key = (name or cls.__name__.removesuffix("Exporter")).strip().lower()
        if not key:
            raise ValueError("nome vazio")
        if key in Exporter.registry:
            raise ValueError(f"exportador já registrado: {key}")
        Exporter.registry[key] = cls

    @classmethod
    def _missing(cls, name):
        available = ", ".join(sorted(Exporter.registry)) or "nenhum"
        return KeyError(f"exportador desconhecido: {name!r}; disponíveis: {available}")

    @classmethod
    def create(cls, name, *args, **kwargs):
        try:
            target = Exporter.registry[name.strip().lower()]
        except KeyError:
            raise cls._missing(name) from None
        return target(*args, **kwargs)

    @classmethod
    def names(cls):
        return sorted(Exporter.registry)

    @classmethod
    def unregister(cls, name):
        try:
            return Exporter.registry.pop(name.strip().lower())
        except KeyError:
            raise cls._missing(name) from None

    @classmethod
    def for_extension(cls, ext):
        for key in sorted(Exporter.registry):
            if Exporter.registry[key].extension.lower() == ext.lower():
                return Exporter.registry[key]
        raise KeyError(f"nenhum exportador para {ext!r}")

    def export(self, rows):
        raise NotImplementedError
