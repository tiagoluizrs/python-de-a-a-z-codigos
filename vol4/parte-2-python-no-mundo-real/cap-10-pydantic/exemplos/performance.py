"""O custo da validação, medido."""
import dataclasses
import json
import time

import attrs
import msgspec
from pydantic import BaseModel, TypeAdapter

N = 100_000
data = [{"id": i, "name": f"n{i}", "tags": ["a", "b"]} for i in range(N)]
raw = json.dumps(data)


class M(BaseModel):
    id: int
    name: str
    tags: list[str]


@dataclasses.dataclass
class D:
    id: int
    name: str
    tags: list[str]


@attrs.define
class A:
    id: int = attrs.field(validator=attrs.validators.instance_of(int))
    name: str = attrs.field(validator=attrs.validators.instance_of(str))
    tags: list = attrs.field(validator=attrs.validators.instance_of(list))


class S(msgspec.Struct):
    id: int
    name: str
    tags: list[str]


def manual(d):
    if not isinstance(d["id"], int) or not isinstance(d["name"], str) or not isinstance(d["tags"], list) or not all(isinstance(x, str) for x in d["tags"]):
        raise TypeError("inválido")
    return D(**d)


def timed(label, func):
    start = time.perf_counter()
    func()
    elapsed = time.perf_counter() - start
    print(f"  {label:<52}{elapsed * 1e3:8.1f} ms | {elapsed / N * 1e6:5.2f} us por objeto")
    return elapsed


print(f"{N:,} objetos de 3 campos (um deles uma lista de 2 textos), dicionários Python -> objetos:")
base = timed("dataclass SEM validar", lambda: [D(**d) for d in data])
timed("validação manual (isinstance) + dataclass", lambda: [manual(d) for d in data])
timed("attrs com validators", lambda: [A(**d) for d in data])
timed("Pydantic: M(**d)", lambda: [M(**d) for d in data])
pyd = timed("Pydantic: M.model_validate(d)", lambda: [M.model_validate(d) for d in data])
print(f"  -> validar com o Pydantic custa {pyd / base:.0f}x o de criar uma dataclass sem validar, mas cada objeto leva ~{pyd / N * 1e6:.1f} us")

print(f"\nde JSON (texto de {len(raw) / 1e6:.1f} MB) até os objetos validados:")
timed("json.loads + M.model_validate em laço", lambda: [M.model_validate(d) for d in json.loads(raw)])
timed("TypeAdapter(list[M]).validate_json (parse e valida no Rust)", lambda: TypeAdapter(list[M]).validate_json(raw))
timed("msgspec.json.decode(type=list[S])", lambda: msgspec.json.decode(raw, type=list[S]))

print("\nmodel_construct (SEM validação, para dados JÁ confiáveis):", end=" ")
construct = timed("M.model_construct(**d)", lambda: [M.model_construct(**d) for d in data])
print("  (nem sempre ganha do validate: confira antes de trocar uma garantia por um palpite)")
print("\nregra: valide na FRONTEIRA (entrada de rede, arquivo, formulário) e passe objetos já validados para dentro; não valide de novo a cada função.")
