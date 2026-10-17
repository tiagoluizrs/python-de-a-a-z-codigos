"""Exercício 6: extrair a assinatura de uma função (gabarito)."""
import inspect


def _name(annotation):
    if annotation is inspect.Parameter.empty:
        return None
    if isinstance(annotation, type):
        return annotation.__name__
    return str(annotation)


def signature_dict(func):
    try:
        sig = inspect.signature(func)
    except ValueError:
        # builtins sem metadados (ex.: max) não têm assinatura
        return None
    params = []
    for p in sig.parameters.values():
        has_default = p.default is not p.empty
        variadic = p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD)
        params.append({
            "name": p.name,
            "kind": p.kind.name,
            "required": not has_default and not variadic,
            "default": p.default if has_default else None,
            "annotation": _name(p.annotation),
        })
    return {"params": params, "returns": _name(sig.return_annotation)}
