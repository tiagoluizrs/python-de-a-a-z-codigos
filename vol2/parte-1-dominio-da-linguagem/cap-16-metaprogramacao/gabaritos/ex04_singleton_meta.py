"""Gabarito do exercício 4."""


class Singleton(type):
    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        key = cls
        if key in Singleton._instances:
            instance, first = Singleton._instances[key]
            if (args, kwargs) != first and (args or kwargs):
                raise TypeError(f"{cls.__name__} já foi criado com outros argumentos")
            return instance
        instance = super().__call__(*args, **kwargs)
        Singleton._instances[key] = (instance, (args, kwargs))
        return instance

    @staticmethod
    def reset(cls):
        Singleton._instances.pop(cls, None)
