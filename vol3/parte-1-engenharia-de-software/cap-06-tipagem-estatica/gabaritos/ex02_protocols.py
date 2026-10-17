"""Gabarito do exercício 2."""
import math
from collections.abc import Iterable
from typing import Protocol, runtime_checkable


class SupportsArea(Protocol):
    def area(self) -> float: ...


@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return math.pi * self.radius**2


class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side**2


def total_area(shapes: Iterable[SupportsArea]) -> float:
    return sum(shape.area() for shape in shapes)


def close_all(resources: Iterable[Closeable]) -> list[str]:
    errors: list[str] = []
    for resource in resources:
        try:
            resource.close()
        except Exception as error:
            errors.append(str(error))
    return errors
