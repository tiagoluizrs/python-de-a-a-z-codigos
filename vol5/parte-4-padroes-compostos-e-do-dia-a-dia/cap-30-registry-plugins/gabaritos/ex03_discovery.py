"""Gabarito do exercício 3."""
import importlib
import importlib.metadata
import pkgutil
from dataclasses import dataclass, field

SUPPORTED_API = 2


@dataclass
class Discovery:
    plugins: dict = field(default_factory=dict)
    errors: dict = field(default_factory=dict)


def discover(package_name):
    package = importlib.import_module(package_name)
    if not hasattr(package, "__path__"):
        raise ValueError(f"{package_name} não é um pacote")
    found, errors, owner = {}, {}, {}
    for info in pkgutil.iter_modules(package.__path__):
        if info.name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"{package_name}.{info.name}")
        except Exception as error:
            errors[info.name] = f"{type(error).__name__}: {error}"
            continue
        name = getattr(module, "NAME", None)
        if not isinstance(name, str) or not name:
            errors[info.name] = "falta NAME"
        elif getattr(module, "API_VERSION", None) != SUPPORTED_API:
            errors[info.name] = f"versão de API não suportada: {getattr(module, 'API_VERSION', None)}"
        elif not callable(getattr(module, "run", None)):
            errors[info.name] = "falta run"
        elif name in found:
            errors[info.name] = f"nome repetido: {name} (já usado por {owner[name]})"
        else:
            found[name] = module
            owner[name] = info.name
    return Discovery(dict(sorted(found.items())), errors)


def load_entry_points(group):
    result = Discovery()
    for entry in sorted(importlib.metadata.entry_points(group=group), key=lambda e: (e.name, e.value)):
        if entry.name in result.plugins or entry.name in result.errors:
            result.errors[entry.name] = f"nome repetido: {entry.name}"
            continue
        try:
            result.plugins[entry.name] = entry.load()
        except Exception as error:
            result.errors[entry.name] = f"{type(error).__name__}: {error}"
    return result
