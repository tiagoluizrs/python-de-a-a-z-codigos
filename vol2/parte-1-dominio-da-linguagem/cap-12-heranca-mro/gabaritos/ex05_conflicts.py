"""Gabarito do exercício 5."""


def find_overrides(cls):
    owners = {}
    for klass in cls.__mro__:
        if klass is object:
            continue
        for name, value in vars(klass).items():
            if name.startswith("__") or not callable(value):
                continue
            owners.setdefault(name, []).append(klass.__name__)
    return {name: classes for name, classes in owners.items() if len(classes) > 1}
