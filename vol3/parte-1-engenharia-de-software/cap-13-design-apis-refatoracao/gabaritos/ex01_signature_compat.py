"""Gabarito do exercício 1."""
import inspect

P = inspect.Parameter


def breaking_changes(old, new):
    old_params = inspect.signature(old).parameters
    new_params = inspect.signature(new).parameters
    new_has_kwargs = any(p.kind is P.VAR_KEYWORD for p in new_params.values())
    new_has_args = any(p.kind is P.VAR_POSITIONAL for p in new_params.values())
    problems = set()
    for name, param in old_params.items():
        if param.kind in (P.VAR_POSITIONAL, P.VAR_KEYWORD):
            continue
        if name not in new_params:
            positional_only = param.kind is P.POSITIONAL_ONLY
            if (param.kind is P.KEYWORD_ONLY and new_has_kwargs) or (positional_only and new_has_args):
                continue
            problems.add(f"removed: {name}")
            continue
        other = new_params[name]
        if param.default is not P.empty and other.default is P.empty:
            problems.add(f"lost-default: {name}")
        if param.kind is P.POSITIONAL_OR_KEYWORD and other.kind in (P.KEYWORD_ONLY, P.POSITIONAL_ONLY):
            problems.add(f"kind: {name}")
        if param.kind is P.POSITIONAL_ONLY and other.kind is P.KEYWORD_ONLY:
            problems.add(f"kind: {name}")
    for name, param in new_params.items():
        if name in old_params or param.kind in (P.VAR_POSITIONAL, P.VAR_KEYWORD):
            continue
        if param.default is P.empty:
            problems.add(f"new-required: {name}")
    old_pos = [n for n, p in old_params.items() if p.kind in (P.POSITIONAL_ONLY, P.POSITIONAL_OR_KEYWORD)]
    new_pos = [n for n, p in new_params.items() if p.kind in (P.POSITIONAL_ONLY, P.POSITIONAL_OR_KEYWORD)]
    common_old = [n for n in old_pos if n in new_pos]
    common_new = [n for n in new_pos if n in old_pos]
    for index, name in enumerate(common_old):
        if common_new[index] != name:
            problems.add(f"reordered: {name}")
    return sorted(problems)
