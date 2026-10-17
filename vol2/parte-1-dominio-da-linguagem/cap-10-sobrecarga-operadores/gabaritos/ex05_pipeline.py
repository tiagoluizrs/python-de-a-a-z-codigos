"""Gabarito do exercício 5."""


class Step:
    def __init__(self, func, name=None):
        self.func = func
        self.name = name or getattr(func, "__name__", repr(func))

    def __call__(self, value):
        return self.func(value)

    def __repr__(self):
        return f"Step({self.name})"

    def __or__(self, other):                           # Step | outro
        if isinstance(other, Step):
            second, name = other.func, other.name
        elif callable(other):
            second, name = other, getattr(other, "__name__", repr(other))
        else:
            return NotImplemented
        first = self.func
        return Step(lambda value: second(first(value)), f"{self.name} | {name}")

    def __ror__(self, other):                          # função comum | Step
        if not callable(other):
            return NotImplemented
        return Step(other) | self

    def __rrshift__(self, value):                      # valor >> step
        return self(value)
