"""Gabarito do exercício 4."""


class ResolutionError(Exception):
    pass


def release(text):
    return tuple(int(part) for part in text.split("."))


def satisfies(version, specifier):
    ops = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b,
           "<": lambda a, b: a < b, "==": lambda a, b: a == b, "!=": lambda a, b: a != b}
    v = release(version)
    for clause in filter(None, (c.strip() for c in specifier.split(","))):
        for op in (">=", "<=", "==", "!=", ">", "<"):
            if clause.startswith(op):
                if not ops[op](v, release(clause[len(op):])):
                    return False
                break
        else:
            raise ValueError(clause)
    return True


def resolve(index, requirements):
    def solve(constraints, chosen):
        pending = [name for name in sorted(constraints) if name not in chosen]
        if not pending:
            return chosen
        name = pending[0]
        if name not in index:
            raise ResolutionError(f"pacote desconhecido: {name}")
        candidates = sorted((v for v in index[name] if all(satisfies(v, s) for s in constraints[name])),
                            key=release, reverse=True)
        for version in candidates:
            new_constraints = {k: list(v) for k, v in constraints.items()}
            ok = True
            for dep, spec in index[name][version].items():
                new_constraints.setdefault(dep, []).append(spec)
                if dep in chosen and not satisfies(chosen[dep], spec):
                    ok = False
                    break
            if not ok:
                continue
            try:
                return solve(new_constraints, {**chosen, name: version})
            except ResolutionError:
                continue
        raise ResolutionError(f"sem versão de {name} compatível com {constraints[name]}")

    return solve({name: [spec] for name, spec in requirements.items()}, {})
