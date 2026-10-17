"""Gabarito do exercício 3."""


class Color:
    _instances = {}

    def __new__(cls, name):
        key = name.lower()
        if not key:
            raise ValueError("nome vazio")
        if key not in cls._instances:
            instance = super().__new__(cls)
            instance.name = key               # gravado UMA vez, aqui no __new__
            cls._instances[key] = instance
        return cls._instances[key]

    @classmethod
    def count(cls):
        return len(cls._instances)

    def __repr__(self):
        return f"Color({self.name!r})"
