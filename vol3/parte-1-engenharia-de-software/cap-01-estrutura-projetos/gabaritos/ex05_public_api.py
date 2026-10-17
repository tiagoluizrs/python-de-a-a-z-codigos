"""Gabarito do exercício 5."""
import types


def public_names(module):
    if hasattr(module, "__all__"):
        return sorted(module.__all__)
    return sorted(name for name, value in vars(module).items()
                  if not name.startswith("_") and not isinstance(value, types.ModuleType))


def broken_exports(module):
    return sorted(name for name in getattr(module, "__all__", ()) if not hasattr(module, name))


def star_import_names(module):
    broken = set(broken_exports(module))
    return [name for name in public_names(module) if name not in broken]
