"""Gabarito do exercício 5."""
import re


class raises:
    def __init__(self, exc_type, match=None):
        self.exc_type, self.match, self.value = exc_type, match, None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            raise AssertionError(f"DID NOT RAISE {self.exc_type.__name__}")
        if not issubclass(exc_type, self.exc_type):
            return False                                     # outro tipo: propaga
        if self.match is not None and not re.search(self.match, str(exc)):
            raise AssertionError(f"texto {str(exc)!r} não casa com {self.match!r}")
        self.value = exc
        return True


def parametrize(argnames, values):
    names = [name.strip() for name in argnames.split(",")]

    def decorate(func):
        func._cases = (names, list(values))
        return func

    return decorate


def _run(func, kwargs):
    try:
        func(**kwargs)
    except AssertionError:
        return "failed"
    except BaseException as error:
        if isinstance(error, (KeyboardInterrupt, SystemExit)):
            raise
        return "error"
    return "passed"


def run_tests(module):
    results = {}
    for name, func in vars(module).items():
        if not (name.startswith("test_") and callable(func)):
            continue
        cases = getattr(func, "_cases", None)
        if cases is None:
            results[name] = _run(func, {})
            continue
        names, values = cases
        for index, value in enumerate(values):
            args = (value,) if len(names) == 1 else tuple(value)
            results[f"{name}[{index}]"] = _run(func, dict(zip(names, args)))
    return results


def summary(results):
    counts = {"passed": 0, "failed": 0, "error": 0}
    for status in results.values():
        counts[status] += 1
    parts = [f"{n} {label}" for label, n in counts.items() if n]
    return ", ".join(parts) if parts else "no tests ran"
