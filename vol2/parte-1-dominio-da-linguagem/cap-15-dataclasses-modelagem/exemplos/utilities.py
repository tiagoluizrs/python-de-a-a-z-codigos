"""asdict, astuple, fields, replace, make_dataclass, is_dataclass."""
import dataclasses
from dataclasses import asdict, astuple, dataclass, field, fields, make_dataclass


@dataclass
class Address:
    city: str
    zip: str


@dataclass
class Person:
    name: str
    address: Address
    tags: list[str] = field(default_factory=list)


p = Person("Ana", Address("Recife", "50000"), ["a", "b"])
print(asdict(p))
print(astuple(p))
print([f.name for f in fields(p)], dataclasses.is_dataclass(p), dataclasses.is_dataclass(Person))

# asdict copia em profundidade
d = asdict(p)
d["tags"].append("c")
print(p.tags, d["tags"])

# Criar uma dataclass em tempo de execução
Dynamic = make_dataclass("Dynamic", [("a", int), ("b", str, field(default="x"))])
print(Dynamic(1), Dynamic.__name__)


# metadata: informação própria dos campos, para serializadores e validadores
@dataclass
class Column:
    name: str = field(metadata={"label": "Nome", "width": 20})
    qty: int = field(default=0, metadata={"label": "Qtd"})


print([(f.name, dict(f.metadata)) for f in fields(Column)])
