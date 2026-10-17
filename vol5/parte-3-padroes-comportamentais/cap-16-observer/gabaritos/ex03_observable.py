"""Gabarito do exercício 3."""


class observed:
    def __init__(self, default=None, validate=None):
        self.default, self.validate, self.name = default, validate, "?"

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, owner=None):
        if obj is None:
            return self
        return obj.__dict__.get("_" + self.name, self.default)

    def __set__(self, obj, value):
        if self.validate is not None:
            self.validate(value)
        old = self.__get__(obj)
        if value == old:
            return
        obj.__dict__["_" + self.name] = value
        for callback in list(obj.__dict__.get("_watchers", {}).get(self.name, [])):
            callback(obj, self.name, old, value)


def watch(obj, name, callback):
    if not isinstance(_lookup(type(obj), name), observed):
        raise AttributeError(f"{name!r} não é observável")
    if not callable(callback):
        raise TypeError("callback precisa ser chamável")
    obj.__dict__.setdefault("_watchers", {}).setdefault(name, []).append(callback)
    return callback


def _lookup(cls, name):
    for klass in cls.__mro__:
        if name in klass.__dict__:
            return klass.__dict__[name]
    return None


def unwatch(obj, name, callback):
    callbacks = obj.__dict__.get("_watchers", {}).get(name, [])
    if callback not in callbacks:
        raise ValueError("não registrado")
    callbacks.remove(callback)
