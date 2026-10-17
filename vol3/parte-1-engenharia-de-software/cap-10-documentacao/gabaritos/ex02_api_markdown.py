"""Gabarito do exercício 2."""
import inspect


def _summary(obj):
    doc = inspect.getdoc(obj)
    return doc.splitlines()[0] if doc else "(sem documentação)"


def _signature(obj):
    try:
        return str(inspect.signature(obj))
    except (TypeError, ValueError):
        return "()"


def module_to_markdown(module):
    lines = [f"# {module.__name__}", "", _summary(module), ""]
    if hasattr(module, "__all__"):
        names = sorted(module.__all__)
    else:
        names = sorted(n for n, o in vars(module).items() if not n.startswith("_") and getattr(o, "__module__", None) == module.__name__)
    for name in names:
        obj = getattr(module, name)
        is_class = inspect.isclass(obj)
        lines += [f"## `{name}{_signature(obj)}` ({'classe' if is_class else 'função'})", "", _summary(obj), ""]
        if is_class:
            methods = sorted((n, m) for n, m in inspect.getmembers(obj, inspect.isfunction) if not n.startswith("_"))
            for method_name, method in methods:
                lines.append(f"- `{method_name}{_signature(method)}`: {_summary(method)}")
            if methods:
                lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"
