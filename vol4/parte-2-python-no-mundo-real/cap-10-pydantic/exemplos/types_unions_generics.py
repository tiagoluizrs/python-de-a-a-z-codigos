"""Tipos reutilizáveis, uniões discriminadas, genéricos, TypeAdapter, from_attributes."""
import dataclasses
from typing import Annotated, Literal, TypedDict

from pydantic import BaseModel, Field, RootModel, TypeAdapter, ValidationError, computed_field

# 1. Annotated: uma restrição, nomeada, reutilizada em vários campos
Percent = Annotated[float, Field(ge=0, le=100)]
Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", max_length=50)]


class Course(BaseModel):
    slug: Slug
    progress: Percent


print("Annotated reutilizável:", Course(slug="python-de-a-a-z", progress="87.5"))
for bad in ({"slug": "Python Maiúsculo", "progress": 50}, {"slug": "ok", "progress": 120}):
    try:
        Course(**bad)
    except ValidationError as error:
        print("  recusado:", error.errors()[0]["loc"], error.errors()[0]["type"])


# 2. união DISCRIMINADA: o campo "kind" decide qual modelo valida (mensagens claras e mais rápido)
class Circle(BaseModel):
    kind: Literal["circle"]
    radius: float

    @computed_field
    @property
    def area(self) -> float:
        return round(3.14159 * self.radius**2, 2)


class Rect(BaseModel):
    kind: Literal["rect"]
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height


Shape = Annotated[Circle | Rect, Field(discriminator="kind")]
shapes = TypeAdapter(list[Shape]).validate_python([{"kind": "circle", "radius": 2}, {"kind": "rect", "width": 3, "height": "4"}])
print("\nunião discriminada:", [(s.kind, s.area) for s in shapes])
try:
    TypeAdapter(Shape).validate_python({"kind": "triangulo", "base": 1})
except ValidationError as error:
    item = error.errors()[0]
    print("kind desconhecido:", item["type"], "|", item["msg"][:70])
try:
    TypeAdapter(Shape).validate_python({"kind": "rect", "width": "x"})
except ValidationError as error:
    print("sem discriminador seriam N erros confusos; com ele, só os do modelo certo:", [e["loc"] for e in error.errors()])


# 3. genéricos
class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int = 1


page = Page[Course].model_validate({"items": [{"slug": "a", "progress": 1}], "total": 1})
print("\nPage[Course]:", page.items[0].slug, "| Page[int]:", Page[int](items=["1", 2], total=2).items)


# 4. TypeAdapter: validar QUALQUER tipo, sem criar uma classe
print("\nTypeAdapter(dict[str, list[int]]):", TypeAdapter(dict[str, list[int]]).validate_python({"a": ["1", 2]}))


class Movie(TypedDict):
    title: str
    year: int


print("TypedDict:", TypeAdapter(Movie).validate_python({"title": "X", "year": "1999"}))


@dataclasses.dataclass
class Point:
    x: int
    y: int


print("dataclass:", TypeAdapter(Point).validate_python({"x": "1", "y": 2}))


# 5. RootModel e from_attributes (objetos de ORM, Capítulo 5)
class Tags(RootModel[list[str]]):
    pass


print("\nRootModel:", Tags(["a", "b"]).root, Tags.model_validate_json('["x", "y"]').root)


class UserRow:                                    # parece um objeto do SQLAlchemy
    def __init__(self):
        self.id, self.name = 1, "Ana"


class UserOut(BaseModel):
    id: int
    name: str


print("from_attributes (ORM -> modelo de saída):", UserOut.model_validate(UserRow(), from_attributes=True))
print("JSON Schema do modelo (OpenAPI, formulários, documentação):", Course.model_json_schema()["properties"]["progress"])
