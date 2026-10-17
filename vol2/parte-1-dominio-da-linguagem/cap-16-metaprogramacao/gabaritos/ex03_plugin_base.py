"""Gabarito do exercício 3."""


class Exporter:
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, fmt=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if fmt is None:
            raise TypeError(f"{cls.__name__}: o argumento fmt é obrigatório")
        if not callable(getattr(cls, "export", None)):
            raise TypeError(f"{cls.__name__} precisa definir export()")
        if fmt in Exporter._registry:
            raise ValueError(f"formato repetido: {fmt}")
        Exporter._registry[fmt] = cls

    @classmethod
    def for_format(cls, fmt):
        return Exporter._registry[fmt]()

    @classmethod
    def formats(cls):
        return sorted(Exporter._registry)
