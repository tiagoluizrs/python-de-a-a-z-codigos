"""Gabarito do exercício 4."""


class Borg:
    _shared: dict = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._shared = {}

    def __init__(self):
        self.__dict__ = type(self)._shared

    @classmethod
    def reset_state(cls):
        cls._shared.clear()

    def __eq__(self, other):
        return type(self) is type(other)

    def __hash__(self):
        return hash(type(self))
