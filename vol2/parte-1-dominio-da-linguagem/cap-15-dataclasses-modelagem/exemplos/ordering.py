"""order=True e ordenação por campos selecionados."""
from dataclasses import dataclass, field


@dataclass(order=True)
class Version:
    major: int
    minor: int
    patch: int = 0


versions = [Version(1, 10), Version(1, 9, 2), Version(2, 0), Version(1, 9)]
print(sorted(versions))
print(Version(1, 9) < Version(1, 10), max(versions))
try:
    Version(1, 0) < (1, 0, 0)
except TypeError as error:
    print("TypeError:", error)


# Ordenar por UM campo e ignorar os outros: sort_index + compare=False
@dataclass(order=True)
class Task:
    sort_index: int = field(init=False, repr=False)
    priority: int = field(compare=False)
    name: str = field(compare=False)

    def __post_init__(self):
        self.sort_index = -self.priority                 # prioridade alta primeiro


tasks = [Task(1, "limpar"), Task(5, "deploy"), Task(3, "revisar")]
print([t.name for t in sorted(tasks)])
