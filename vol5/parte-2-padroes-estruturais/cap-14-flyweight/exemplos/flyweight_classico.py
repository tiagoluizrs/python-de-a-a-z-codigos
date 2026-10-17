"""Flyweight, forma clássica (GoF): COMPARTILHAR o estado que se repete entre muitos objetos, para gastar menos memória."""
import random
import tracemalloc
from dataclasses import dataclass


def memory_of(build):
    """Bytes que o objeto devolvido por build() ocupa (medido com tracemalloc; o resultado fica referenciado durante a medida)."""
    tracemalloc.start()
    before = tracemalloc.get_traced_memory()[0]
    result = build()
    used = tracemalloc.get_traced_memory()[0] - before
    tracemalloc.stop()
    return used, result


# --- 1. o problema: 50.000 árvores, cada uma com a sua cópia de dados que se REPETEM (espécie, cor, textura) ---
SPECIES = [("carvalho", "verde-escuro"), ("pinheiro", "verde"), ("bétula", "verde-claro")]


class TreeHeavy:
    def __init__(self, species, color, x, y):
        self.species, self.color = species, color
        self.texture = bytes(range(256)) * 8                       # 2 KiB de "textura": uma CÓPIA por árvore
        self.x, self.y = x, y


def forest_heavy(n):
    rng = random.Random(1)
    out = []
    for _ in range(n):
        species, color = rng.choice(SPECIES)
        out.append(TreeHeavy("".join(species), "".join(color), rng.random(), rng.random()))
    return out


# --- 2. o Flyweight: separar o estado INTRÍNSECO (compartilhado, imutável) do EXTRÍNSECO (de cada objeto) ---
@dataclass(frozen=True)
class TreeType:                                                    # o flyweight: dados que se repetem, imutáveis
    species: str
    color: str
    texture: bytes


class TreeTypeFactory:                                             # a fábrica: devolve o MESMO flyweight para os mesmos dados
    _types: dict = {}

    @classmethod
    def get(cls, species, color):
        key = (species, color)
        if key not in cls._types:
            cls._types[key] = TreeType(species, color, bytes(range(256)) * 8)
        return cls._types[key]


class Tree:                                                        # o contexto: só o estado EXTRÍNSECO (posição) e uma referência ao flyweight
    def __init__(self, tree_type, x, y):
        self.type, self.x, self.y = tree_type, x, y


def forest_flyweight(n):
    rng = random.Random(1)
    out = []
    for _ in range(n):
        species, color = rng.choice(SPECIES)
        out.append(Tree(TreeTypeFactory.get("".join(species), "".join(color)), rng.random(), rng.random()))
    return out


N = 50_000
heavy_bytes, heavy = memory_of(lambda: forest_heavy(N))
fly_bytes, fly = memory_of(lambda: forest_flyweight(N))
print(f"{N:,} árvores sem flyweight: {heavy_bytes / 1e6:7.1f} MB ({heavy_bytes / N:,.0f} bytes por árvore)")
print(f"{N:,} árvores com flyweight: {fly_bytes / 1e6:7.1f} MB ({fly_bytes / N:,.0f} bytes por árvore) | {heavy_bytes / fly_bytes:.0f}x menos memória")
print("tipos de árvore distintos criados:", len(TreeTypeFactory._types), "| o mesmo objeto para árvores da mesma espécie:", fly[0].type is next(t for t in fly[1:] if t.type == fly[0].type).type)

# --- 3. a regra de ouro: o flyweight é IMUTÁVEL (ele é compartilhado por milhares de contextos) ---
try:
    fly[0].type.color = "vermelho"                                 # type: ignore[misc]
except Exception as error:
    print("\nmutar um flyweight compartilhado é recusado:", type(error).__name__)


class BadType:
    def __init__(self, color):
        self.color = color


shared = BadType("verde")
a, b = Tree(shared, 0, 0), Tree(shared, 1, 1)
a.type.color = "vermelho"                                          # "só a árvore a"... mas o flyweight é de todas
print("com um flyweight MUTÁVEL, mudar 'a' muda 'b' também:", b.type.color, "(o bug clássico do padrão)")

# --- 4. o ganho existe porque os dados repetidos são GRANDES: com dados pequenos, o ganho some ---
class PointHeavy:
    def __init__(self, label, x, y):
        self.label, self.x, self.y = label, x, y


small_n = 50_000
small_bytes, _small = memory_of(lambda: [PointHeavy("origem", i, i) for i in range(small_n)])
print(f"\npontos com um rótulo curto repetido ({small_n:,}): {small_bytes / small_n:,.0f} bytes por objeto: a repetição de uma string interna já é compartilhada pelo Python")
print("flyweight compensa quando o estado repetido é GRANDE (2 KiB aqui) e as combinações distintas são POUCAS (3 de 50.000)")
