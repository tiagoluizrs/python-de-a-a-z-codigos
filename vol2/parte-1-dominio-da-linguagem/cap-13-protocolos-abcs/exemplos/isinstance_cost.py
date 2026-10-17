"""O custo do isinstance com tipos concretos, ABCs e protocolos."""
import timeit
from collections import abc
from typing import Protocol, runtime_checkable


@runtime_checkable
class HasLen(Protocol):
    def __len__(self) -> int: ...


class Plain:
    def __len__(self):
        return 3


items = [1, 2]
plain = Plain()
ns = {"x": items, "p": plain, "abc": abc, "list": list, "HasLen": HasLen}
cases = [
    ("isinstance(x, list)", "isinstance(x, list)"),
    ("isinstance(x, abc.Sequence)  (herança/registro)", "isinstance(x, abc.Sequence)"),
    ("isinstance(x, abc.Sized)  (estrutural)", "isinstance(x, abc.Sized)"),
    ("isinstance(p, abc.Sized)  (estrutural, 1a classe)", "isinstance(p, abc.Sized)"),
    ("isinstance(p, HasLen)  (Protocol runtime)", "isinstance(p, HasLen)"),
    ("hasattr(p, '__len__')", "hasattr(p, '__len__')"),
]
for label, statement in cases:
    seconds = min(timeit.repeat(statement, globals=ns, number=300_000,
                                repeat=5)) / 300_000
    print(f"{label:<52}{seconds * 1e9:8.1f} ns")
