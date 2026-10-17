"""lambda e anotações adiadas (3.14)."""
import annotationlib

names = ["bob", "Alice", "carol"]
print(sorted(names, key=lambda s: s.lower()))
f = lambda x: x
print(f.__name__)


def late(arg: Undefined) -> Later:
    return arg


print(late.__annotations__ if False else "not evaluated yet")
try:
    late.__annotations__
except NameError as exc:
    print("NameError:", exc)
print(annotationlib.get_annotations(
    late, format=annotationlib.Format.STRING))


class Later:
    pass
