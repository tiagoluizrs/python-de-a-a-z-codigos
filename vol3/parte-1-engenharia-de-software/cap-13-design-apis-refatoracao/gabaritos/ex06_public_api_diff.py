"""Gabarito do exercício 6."""
import inspect


def _signature(obj):
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return "(...)"


def public_api(module):
    if hasattr(module, "__all__"):
        names = [n for n in module.__all__ if hasattr(module, n)]
    else:
        names = [n for n, o in vars(module).items() if not n.startswith("_") and (inspect.isfunction(o) or inspect.isclass(o))
                 and getattr(o, "__module__", None) == module.__name__]
    return {name: _signature(getattr(module, name)) for name in names}


def diff_api(old, new):
    return {"removed": sorted(set(old) - set(new)), "added": sorted(set(new) - set(old)),
            "changed": sorted(n for n in set(old) & set(new) if old[n] != new[n])}


def required_bump(diff):
    if diff["removed"] or diff["changed"]:
        return "major"
    return "minor" if diff["added"] else "patch"
