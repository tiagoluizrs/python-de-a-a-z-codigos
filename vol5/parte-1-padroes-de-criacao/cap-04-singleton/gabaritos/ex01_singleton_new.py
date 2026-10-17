"""Gabarito do exercício 1."""


class Config:
    created = 0

    def __new__(cls, values=None):
        instance = cls.__dict__.get("_instance")
        if instance is None:
            instance = super().__new__(cls)
            instance._values = dict(values or {})
            cls._instance = instance
            cls.created = cls.__dict__.get("created", 0) + 1
        elif values is not None:
            raise ValueError("Config já foi criada; use set()")
        return instance

    def get(self, key, default=None):
        return self._values.get(key, default)

    def set(self, key, value):
        self._values[key] = value

    @classmethod
    def reset_for_tests(cls):
        if "_instance" in cls.__dict__:
            del cls._instance
