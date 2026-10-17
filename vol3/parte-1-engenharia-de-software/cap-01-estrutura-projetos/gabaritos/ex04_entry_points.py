"""Gabarito do exercício 4."""
import importlib


def parse_entry_point(spec):
    if spec.count(":") != 1 or any(ch.isspace() for ch in spec):
        raise ValueError(f"ponto de entrada inválido: {spec!r}")
    module, attr = spec.split(":")
    if not module or not attr:
        raise ValueError(f"ponto de entrada inválido: {spec!r}")
    return module, attr


def load_entry_point(spec):
    module_name, attr = parse_entry_point(spec)
    obj = importlib.import_module(module_name)
    for part in attr.split("."):
        obj = getattr(obj, part)
    return obj


def run_entry_point(spec, argv):
    result = load_entry_point(spec)(argv)
    if result is None:
        return 0
    if isinstance(result, int):
        return result
    return 1
