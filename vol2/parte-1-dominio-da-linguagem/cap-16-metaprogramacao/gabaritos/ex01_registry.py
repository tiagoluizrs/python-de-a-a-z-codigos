"""Gabarito do exercício 1."""

HANDLERS: dict[str, type] = {}


def handler(name):
    def decorate(cls):
        if name in HANDLERS:
            raise ValueError(f"handler repetido: {name}")
        HANDLERS[name] = cls
        cls.handler_name = name
        return cls
    return decorate
