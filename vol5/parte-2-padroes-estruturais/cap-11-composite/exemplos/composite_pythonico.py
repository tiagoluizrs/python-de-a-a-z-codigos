"""Composite em Python: um dataclass com uma lista de filhos, __iter__ com yield from, e a pegadinha do limite de recursão."""
import sys
import time
import xml.etree.ElementTree as ET
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
import tempfile


# --- 1. a estrutura em dados: UM tipo, com filhos opcionais (a folha é um nó sem filhos) ---
@dataclass
class Node:
    name: str
    size: int = 0                                              # só as folhas têm tamanho próprio
    children: list = field(default_factory=list)

    def total(self) -> int:                                    # a mesma operação para folha e galho: a folha soma uma lista vazia
        return self.size + sum(child.total() for child in self.children)

    def __iter__(self):                                        # o protocolo de iteração: percorrer a árvore em profundidade
        yield self
        for child in self.children:
            yield from child

    def __len__(self):
        return sum(1 for _ in self)

    def __contains__(self, name):
        return any(node.name == name for node in self)


root = Node("projeto", children=[Node("README.md", 120), Node("src", children=[Node("main.py", 800), Node("util.py", 300)])])
print("um tipo só:", root.total(), "bytes | nós:", len(root), "| 'util.py' in root:", "util.py" in root)
print("for/list/sum/any funcionam sobre a árvore sem código extra:", [n.name for n in root])
print("arquivos .py:", [n.name for n in root if n.name.endswith(".py")], "| maior arquivo:", max(root, key=lambda n: n.size).name)

# --- 2. a pegadinha: a recursão tem limite (e os geradores aninhados custam O(profundidade) por item) ---
def chain(depth):
    head = Node("n0", 1)
    cur = head
    for i in range(1, depth):
        nxt = Node(f"n{i}", 1)
        cur.children.append(nxt)
        cur = nxt
    return head


print("\nlimite de recursão do Python:", sys.getrecursionlimit())
deep = chain(5000)
try:
    deep.total()
except RecursionError as error:
    print("total() recursivo em uma cadeia de 5.000 nós:", type(error).__name__, "->", str(error)[:50])


def iterative_nodes(top):
    stack = [top]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(node.children))                  # reversed: mantém a ordem da recursão


def iterative_total(top):
    return sum(node.size for node in iterative_nodes(top))


print("versão iterativa (pilha explícita) na mesma cadeia:", iterative_total(deep), "| nós:", sum(1 for _ in iterative_nodes(deep)))


def max_recursive_depth():
    low, high = 1, 5000
    while low < high:                                          # busca binária da maior cadeia em que total() ainda funciona
        mid = (low + high + 1) // 2
        try:
            chain(mid).total()
            low = mid
        except RecursionError:
            high = mid - 1
    return low


print("maior profundidade que total() recursivo aguenta:", max_recursive_depth(), "(cada nível gasta DOIS quadros: o método e a expressão geradora)")


# --- 3. o custo: recursivo, gerador aninhado e iterativo, em uma árvore larga e em uma funda ---
def build(depth, width):
    n = Node(f"d{depth}", 1)
    if depth > 0:
        n.children = [build(depth - 1, width) for _ in range(width)]
    return n


def best(fn, n=20):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e3


wide = build(4, 8)                                             # 4.681 nós, profundidade 5
medium = chain(400)                                            # profundidade 400 (dentro do limite)
count_wide = len(wide)
print(f"\n{count_wide} nós, profundidade 5:")
print(f"  total() recursivo          {best(wide.total):6.2f} ms")
print(f"  sum sobre iter (yield from) {best(lambda: sum(n.size for n in wide)):6.2f} ms")
print(f"  sum sobre pilha explícita   {best(lambda: iterative_total(wide)):6.2f} ms")
print("400 nós em cadeia (profundidade 400):")
print(f"  total() recursivo          {best(medium.total):6.2f} ms")
print(f"  sum sobre iter (yield from) {best(lambda: sum(n.size for n in medium)):6.2f} ms  (cada item atravessa até 400 geradores aninhados)")
print(f"  sum sobre pilha explícita   {best(lambda: iterative_total(medium)):6.2f} ms")

# --- 4. a biblioteca padrão: ElementTree é um Composite (o Element tem filhos Element); pathlib percorre pastas ---
doc = ET.fromstring("<menu><item price='5'>café</item><group><item price='3'>pão</item><item price='4'>bolo</item></group></menu>")
print("\nxml.etree.ElementTree: o mesmo Element para a raiz, o grupo e a folha ->", [e.tag for e in doc.iter()], "| soma:", sum(int(e.get("price")) for e in doc.iter("item")))

folder = Path(tempfile.mkdtemp())
(folder / "a").mkdir()
(folder / "a" / "x.txt").write_text("12345", encoding="utf-8")
(folder / "y.txt").write_text("123", encoding="utf-8")
print("pathlib.rglob percorre a árvore de pastas:", sum(p.stat().st_size for p in folder.rglob("*") if p.is_file()), "bytes em", len(list(folder.rglob("*.txt"))), "arquivos")

import ast  # noqa: E402

print("o módulo ast também: uma expressão é uma árvore de nós com a mesma interface ->", [type(n).__name__ for n in ast.walk(ast.parse("1 + 2 * 3", mode="eval"))])

# --- 5. tamanho em cache: invalidar quando a árvore muda (a pegadinha do cached_property) ---
class Cached:
    def __init__(self, name, size=0):
        self.name, self._size, self.children, self.parent, self._total = name, size, [], None, None

    def add(self, child):
        child.parent = self
        self.children.append(child)
        self._invalidate()
        return self

    def _invalidate(self):
        node = self
        while node is not None:                                 # a mudança invalida o total deste nó E de todos os ancestrais
            node._total = None
            node = node.parent

    @property
    def total(self):
        if self._total is None:
            self._total = self._size + sum(c.total for c in self.children)
        return self._total


top = Cached("top").add(Cached("a", 10))
leaf_parent = Cached("g")
top.add(leaf_parent)
print("\ntotal com cache:", top.total)
leaf_parent.add(Cached("b", 5))
print("depois de acrescentar um neto, o total do topo foi invalidado e recalculado:", top.total)
