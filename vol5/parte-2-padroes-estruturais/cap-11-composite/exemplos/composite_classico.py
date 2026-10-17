"""Composite, forma clássica (GoF): tratar objetos individuais (folhas) e composições (galhos) PELA MESMA INTERFACE."""
import ast
import inspect
import textwrap
import time
from abc import ABC, abstractmethod


# --- 1. o problema: pastas e arquivos. Quem soma os tamanhos precisa distinguir os dois com isinstance... em todo lugar ---
def total_size_naive(item):
    if isinstance(item, tuple):                                  # um "arquivo": (nome, tamanho)
        return item[1]
    return sum(total_size_naive(child) for child in item["children"])      # uma "pasta": {"children": [...]}


tree_naive = {"children": [("a.txt", 10), {"children": [("b.txt", 5), ("c.txt", 7)]}]}
print("sem o padrão, cada função percorre a estrutura com isinstance:", total_size_naive(tree_naive))


# --- 2. a forma clássica: um componente com a interface COMUM; folhas e composições a implementam ---
class Node(ABC):
    def __init__(self, name):
        self.name, self.parent = name, None

    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def render(self, indent: int = 0) -> str: ...


class File(Node):                                                # a FOLHA
    def __init__(self, name, size):
        super().__init__(name)
        self._size = size

    def size(self):
        return self._size

    def render(self, indent=0):
        return f"{'  ' * indent}{self.name} ({self._size})"


class Directory(Node):                                           # o COMPOSTO: contém componentes (folhas ou outros compostos)
    def __init__(self, name):
        super().__init__(name)
        self.children = []

    def add(self, node):
        node.parent = self
        self.children.append(node)
        return self

    def size(self):
        return sum(child.size() for child in self.children)     # a MESMA chamada, sem distinguir folha de composto

    def render(self, indent=0):
        lines = [f"{'  ' * indent}{self.name}/ ({self.size()})"]
        lines += [child.render(indent + 1) for child in self.children]
        return "\n".join(lines)


root = Directory("projeto").add(File("README.md", 120)).add(
    Directory("src").add(File("main.py", 800)).add(File("util.py", 300)).add(Directory("tests").add(File("test_main.py", 450))))
print("\ncomposite:")
print(root.render())
print("\no cliente chama size() sem saber se é arquivo ou pasta:", File("x", 5).size(), root.children[1].size(), root.size())


# --- 3. as perguntas que o composto responde percorrendo a árvore ---
def walk(node, prefix=""):
    path = f"{prefix}/{node.name}"
    yield path, node
    for child in getattr(node, "children", []):
        yield from walk(child, path)


print("todos os arquivos .py:", [p for p, n in walk(root) if isinstance(n, File) and n.name.endswith(".py")])


# --- 4. o ponto fraco: a interface do composto (add/remove) não existe na folha ---
try:
    File("a", 1).add(File("b", 2))                               # type: ignore[attr-defined]
except AttributeError as error:
    print("\na folha não tem add():", error, "| o GoF discute onde declarar add (no componente: transparência; só no composto: segurança)")


# --- 5. o custo ---
def build(depth, width):
    d = Directory(f"d{depth}")
    for i in range(width):
        d.add(File(f"f{i}", i))
        if depth > 1:
            d.add(build(depth - 1, width))
    return d


big = build(5, 6)
count = sum(1 for _ in walk(big))
start = time.perf_counter()
for _ in range(20):
    big.size()
t = (time.perf_counter() - start) / 20 * 1e3
print(f"\nárvore com {count} nós: size() recursivo leva {t:.2f} ms ({t / count * 1e6:.0f} ns por nó)")


def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("Node + File + Directory:", measure([Node, File, Directory]))
