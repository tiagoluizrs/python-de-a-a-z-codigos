"""Gabarito do exercício 3."""


def auto_repr(cls):
    if "__repr__" in vars(cls):
        return cls

    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in sorted(vars(self).items()))
        return f"{type(self).__name__}({fields})"

    cls.__repr__ = __repr__
    return cls


def register_in(registry, name=None):
    def decorator(cls):
        key = name or cls.__name__
        if key in registry:
            raise ValueError(f"nome já registrado: {key}")
        registry[key] = cls
        return cls

    return decorator


def write_once(*names):
    protected = set(names)

    def decorator(cls):
        def __setattr__(self, key, value):
            if key in protected and key in vars(self):
                raise AttributeError(f"{key} já foi definido")
            super(cls, self).__setattr__(key, value)

        def __delattr__(self, key):
            if key in protected:
                raise AttributeError(f"{key} não pode ser apagado")
            super(cls, self).__delattr__(key)

        cls.__setattr__ = __setattr__
        cls.__delattr__ = __delattr__
        return cls

    return decorator


def add_methods(**methods):
    def decorator(cls):
        for name in methods:
            if hasattr(cls, name):
                raise ValueError(f"{name} já existe em {cls.__name__}")
        for name, function in methods.items():
            setattr(cls, name, function)
        return cls

    return decorator
