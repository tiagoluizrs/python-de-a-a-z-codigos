"""Gabarito do exercício 6."""
import contextlib
import io


def _parse(docstring):
    examples, lines, i = [], docstring.splitlines(), 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith(">>> ") or stripped == ">>>":
            source = [stripped[4:]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("..."):
                source.append(lines[i].strip()[4:] if lines[i].strip().startswith("... ") else "")
                i += 1
            expected = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(">>>"):
                expected.append(lines[i].strip())
                i += 1
            examples.append(("\n".join(source), "\n".join(expected)))
        else:
            i += 1
    return examples


def run_examples(docstring, namespace=None):
    namespace = {} if namespace is None else namespace
    failures = []
    for source, expected in _parse(docstring):
        buffer = io.StringIO()
        error = None
        try:
            with contextlib.redirect_stdout(buffer):
                try:
                    value = eval(compile(source, "<doctest>", "eval"), namespace)
                except SyntaxError:
                    exec(compile(source, "<doctest>", "exec"), namespace)
                else:
                    if value is not None:
                        print(repr(value))
        except Exception as exc:
            error = exc
        got = "\n".join(line.strip() for line in buffer.getvalue().splitlines()).strip()
        if error is not None:
            lines = expected.splitlines()
            ok = bool(lines) and lines[0].startswith("Traceback (most recent call last):") and lines[-1] == f"{type(error).__name__}: {error}"
            if not ok:
                failures.append({"source": source, "expected": expected, "got": f"{type(error).__name__}: {error}"})
        elif got != expected:
            failures.append({"source": source, "expected": expected, "got": got})
    return failures
