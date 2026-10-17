"""Prototype em Python: o padrão inteiro é o módulo copy (copy, deepcopy, replace) e o protocolo __copy__/__deepcopy__."""
import copy
import dataclasses
import datetime as dt
import threading
import time
from dataclasses import dataclass, field


# --- 1. cópia rasa x profunda ---
original = {"name": "base", "tags": ["a", "b"], "limits": {"max": 10}}
shallow = copy.copy(original)
deep = copy.deepcopy(original)
shallow["tags"].append("x")
print("cópia RASA compartilha o que está dentro:  original['tags'] =", original["tags"], "| shallow['tags'] is original['tags']:", shallow["tags"] is original["tags"])
deep["limits"]["max"] = 99
print("cópia PROFUNDA não compartilha:            original['limits'] =", original["limits"], "| deep['limits'] is original['limits']:", deep["limits"] is original["limits"])

# as 'cópias' que não copiam: a atribuição e o fatiamento aninhado
alias = original
print("\natribuição só cria outro nome:", alias is original, "| lista.copy(), dict.copy() e o fatiamento são RASOS (copiam um nível)")
grid_bug = [[0] * 3] * 3
grid_ok = [[0] * 3 for _ in range(3)]
grid_bug[0][0] = 1
grid_ok[0][0] = 1
print("[[0]*3]*3 repete a MESMA linha:", grid_bug, "| com compreensão, linhas independentes:", grid_ok)


# --- 2. um objeto com um recurso que NÃO pode ser copiado: __copy__ e __deepcopy__ ---
class Document:
    def __init__(self, title, sections):
        self.title, self.sections = title, sections
        self._lock = threading.Lock()                          # um recurso do objeto: não é copiável
        self._cache = None                                     # dado derivado: não deve acompanhar a cópia

    def render(self):
        if self._cache is None:
            self._cache = f"{self.title}: " + ", ".join(self.sections)
        return self._cache

    def __copy__(self):
        clone = type(self).__new__(type(self))
        clone.__dict__.update(self.__dict__)                   # raso: compartilha as seções
        clone._lock = threading.Lock()                         # mas o recurso é NOVO
        clone._cache = None
        return clone

    def __deepcopy__(self, memo):
        clone = type(self).__new__(type(self))
        memo[id(self)] = clone                                  # registrar ANTES de copiar o conteúdo: é o que resolve ciclos
        clone.title = self.title
        clone.sections = copy.deepcopy(self.sections, memo)
        clone._lock = threading.Lock()
        clone._cache = None
        return clone


doc = Document("Relatório", ["intro", "dados"])
doc.render()
try:
    copy.deepcopy(threading.Lock())
except TypeError as error:
    print("\numa trava não é copiável:", error)
twin = copy.deepcopy(doc)
twin.sections.append("conclusão")
print("deepcopy com __deepcopy__: seções do original", doc.sections, "| da cópia", twin.sections, "| lock novo:", twin._lock is not doc._lock, "| cache zerado:", twin._cache is None)
shallow_doc = copy.copy(doc)
print("copy com __copy__: compartilha as seções?", shallow_doc.sections is doc.sections, "| lock novo:", shallow_doc._lock is not doc._lock)

# --- 3. ciclos: o memo do deepcopy ---
class Node:
    def __init__(self, name):
        self.name, self.parent, self.children = name, None, []

    def add(self, child):
        child.parent = self
        self.children.append(child)


root = Node("raiz")
root.add(Node("filho"))
clone = copy.deepcopy(root)
print("\nciclo pai<->filho copiado sem recursão infinita:", clone.children[0].parent is clone, "| e sem apontar para o original:", clone.children[0].parent is not root)

# --- 4. a variante de uma linha: dataclasses.replace e copy.replace (3.13+) ---
@dataclass(frozen=True)
class Style:
    font: str = "serif"
    size: int = 12
    tags: tuple = ()


base = Style()
big = dataclasses.replace(base, size=18)
big2 = copy.replace(base, size=24)                              # o mesmo, pelo protocolo __replace__: funciona em dataclasses, namedtuples, datetime...

print("\ndataclasses.replace:", big, "| copy.replace:", big2, "| em datetime:", copy.replace(dt.date(2026, 10, 13), day=1))


# --- 5. o padrão de 'valor padrão compartilhado' que o Prototype tenta evitar ---
@dataclass
class Settings:
    name: str
    flags: list = field(default_factory=list)


default = Settings("padrão", ["a"])
mine = copy.copy(default)
mine.flags.append("b")
print("\ncopy.copy de um dataclass com lista:", default.flags, "(o modelo foi alterado: use deepcopy ou clone os campos mutáveis)")


# --- 6. o custo ---
def best(fn, n=200_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e9


small = {"name": "base", "tags": ["a", "b"], "limits": {"max": 10}}
st = Style("sans", 10, ("x",))
print("\ncusto de obter um objeto pequeno:")
for label, fn in [("construir de novo (Style(...))", lambda: Style("sans", 10, ("x",))), ("dataclasses.replace(st, size=11)", lambda: dataclasses.replace(st, size=11)),
                  ("copy.replace(st, size=11)", lambda: copy.replace(st, size=11)), ("copy.copy(dict)", lambda: copy.copy(small)),
                  ("dict.copy()", small.copy), ("copy.deepcopy(dict aninhado)", lambda: copy.deepcopy(small))]:
    print(f"  {label:<36} {best(fn):7.0f} ns")
print("deepcopy é de longe o mais caro (percorre e registra cada objeto): para estruturas só com listas, números e textos, copiar à mão costuma ser mais rápido")
