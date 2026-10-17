"""Gabarito do exercício 2."""
import operator


def release(text):
    return tuple(int(part) for part in text.split("."))


def _pad(a, b):
    size = max(len(a), len(b))
    return a + (0,) * (size - len(a)), b + (0,) * (size - len(b))


def _compare(op, version, target):
    a, b = _pad(release(version), release(target))
    return {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt,
            "==": operator.eq, "!=": operator.ne}[op](a, b)


def _prefix_match(version, prefix):
    v, p = release(version), release(prefix)
    v = v + (0,) * (len(p) - len(v))
    return v[:len(p)] == p


def satisfies(version, specifier):
    for raw in specifier.split(","):
        clause = raw.strip()
        if not clause:
            continue
        for op in ("~=", ">=", "<=", "==", "!=", ">", "<"):
            if clause.startswith(op):
                target = clause[len(op):].strip()
                break
        else:
            raise ValueError(f"cláusula inválida: {clause!r}")
        try:
            if op == "~=":
                parts = target.split(".")
                if len(parts) < 2:
                    raise ValueError(clause)
                if not (_compare(">=", version, target) and _prefix_match(version, ".".join(parts[:-1]))):
                    return False
            elif op in ("==", "!=") and target.endswith(".*"):
                matched = _prefix_match(version, target[:-2])
                if matched != (op == "=="):
                    return False
            elif not _compare(op, version, target):
                return False
        except ValueError:
            raise ValueError(f"cláusula inválida: {clause!r}") from None
    return True
