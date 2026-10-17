"""Gabarito do exercício 5."""
from abc import ABC, abstractmethod


class Drawable(ABC):
    @abstractmethod
    def draw(self): ...

    @classmethod
    def __subclasshook__(cls, candidate):
        if cls is Drawable:                            # não afeta subclasses de Drawable
            for klass in candidate.__mro__:
                if "draw" in klass.__dict__:
                    return callable(klass.__dict__["draw"])
            return NotImplemented                      # sem draw: herança/register decidem
        return NotImplemented
