"""Gabarito do exercício 3."""
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter, computed_field


class Circle(BaseModel):
    kind: Literal["circle"]
    radius: float = Field(gt=0)

    @computed_field
    @property
    def area(self) -> float:
        return round(3.14159 * self.radius**2, 2)


class Rect(BaseModel):
    kind: Literal["rect"]
    width: float = Field(gt=0)
    height: float = Field(gt=0)

    @computed_field
    @property
    def area(self) -> float:
        return round(self.width * self.height, 2)


class Square(BaseModel):
    kind: Literal["square"]
    side: float = Field(gt=0)

    @computed_field
    @property
    def area(self) -> float:
        return round(self.side**2, 2)


Shape = Annotated[Circle | Rect | Square, Field(discriminator="kind")]
_ADAPTER = TypeAdapter(list[Shape])


def parse_shapes(items):
    return _ADAPTER.validate_python(items)


def total_area(items):
    return round(sum(shape.area for shape in parse_shapes(items)), 2)
