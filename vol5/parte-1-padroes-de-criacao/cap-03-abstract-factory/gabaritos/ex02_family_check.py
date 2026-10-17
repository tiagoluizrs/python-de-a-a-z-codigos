"""Gabarito do exercício 2."""
import inspect


def _params(fn):
    return tuple(inspect.signature(fn).parameters)


def check_families(families):
    if not families:
        return []
    names = list(families)
    reference = families[names[0]]
    problems = []
    for name in names[1:]:
        family = families[name]
        for product in sorted(set(reference) - set(family)):
            problems.append(f"{name}: falta {product!r}")
        for product in sorted(set(family) - set(reference)):
            problems.append(f"{name}: produto extra {product!r}")
        for product in sorted(set(reference) & set(family)):
            fn = family[product]
            if not callable(fn):
                problems.append(f"{name}: {product!r} não é chamável")
                continue
            got, expected = _params(fn), _params(reference[product])
            if got != expected:
                problems.append(f"{name}: {product!r} tem parâmetros ({', '.join(got)}), esperado ({', '.join(expected)})")
    return problems
