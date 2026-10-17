"""Gabarito do exercício 5."""


def capture(func, inputs):
    master = {}
    for args in inputs:
        try:
            master[args] = func(*args)
        except Exception as error:
            master[args] = f"{type(error).__name__}: {error}"
    return master


def diff_masters(old, new):
    return {"changed": {a: (old[a], new[a]) for a in old if a in new and old[a] != new[a]},
            "missing": [a for a in old if a not in new], "extra": [a for a in new if a not in old]}


def refactor_is_safe(old_func, new_func, inputs):
    inputs = list(inputs)
    changed = diff_masters(capture(old_func, inputs), capture(new_func, inputs))["changed"]
    return (not changed, changed)
