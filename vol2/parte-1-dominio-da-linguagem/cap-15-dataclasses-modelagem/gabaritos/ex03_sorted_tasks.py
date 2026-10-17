"""Gabarito do exercício 3."""
from dataclasses import dataclass, field


@dataclass(order=True)
class Task:
    sort_index: tuple = field(init=False, repr=False)
    priority: int = field(compare=False)
    name: str = field(compare=False)
    done: bool = field(default=False, compare=False, repr=False)

    def __post_init__(self):
        self.sort_index = (-self.priority, self.name)            # maior prioridade, depois nome
