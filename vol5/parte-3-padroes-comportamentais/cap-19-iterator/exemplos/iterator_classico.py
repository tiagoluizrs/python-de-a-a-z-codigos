"""Iterator, forma clássica (GoF): percorrer uma coleção SEM expor a sua estrutura interna."""
import ast
import inspect
import textwrap
import time
from abc import ABC, abstractmethod


# --- 1. o problema: o cliente depende da ESTRUTURA da coleção (lista, árvore, lista ligada) ---
class LinkedNode:
    def __init__(self, value, next_node=None):
        self.value, self.next = value, next_node


head = LinkedNode(1, LinkedNode(2, LinkedNode(3)))
node, values = head, []
while node is not None:                                       # o cliente conhece nós e ponteiros
    values.append(node.value)
    node = node.next
print("percorrendo a estrutura 'à mão':", values, "| trocar a lista ligada por um array obriga a reescrever este laço")


# --- 2. a forma clássica (estilo GoF/Java): interface Iterator (has_next/next) e coleção que cria o iterador ---
class Iterator(ABC):
    @abstractmethod
    def has_next(self) -> bool: ...

    @abstractmethod
    def next(self): ...


class LinkedListIterator(Iterator):
    def __init__(self, head):
        self._current = head

    def has_next(self):
        return self._current is not None

    def next(self):
        value = self._current.value
        self._current = self._current.next
        return value


class LinkedList:
    def __init__(self, *values):
        self.head = None
        for value in reversed(values):
            self.head = LinkedNode(value, self.head)

    def create_iterator(self) -> Iterator:
        return LinkedListIterator(self.head)


iterator = LinkedList(10, 20, 30).create_iterator()
collected = []
while iterator.has_next():                                    # o cliente só conhece has_next/next
    collected.append(iterator.next())
print("\nIterator clássico (has_next/next):", collected)


# --- 3. o protocolo do Python: __iter__ e __next__ (e StopIteration no lugar de has_next) ---
class PyListIterator:
    def __init__(self, head):
        self._current = head

    def __iter__(self):
        return self                                           # um iterador é iterável

    def __next__(self):
        if self._current is None:
            raise StopIteration                               # o "fim" é uma exceção, não uma pergunta
        value = self._current.value
        self._current = self._current.next
        return value


class PyLinkedList(LinkedList):
    def __iter__(self):
        return PyListIterator(self.head)                      # iterável: devolve um iterador NOVO a cada chamada


py_list = PyLinkedList(10, 20, 30)
print("\nprotocolo __iter__/__next__:", list(py_list), "| for, list, sum, max, in: todos funcionam;", 20 in py_list, sum(py_list))
print("e iterável pode ser percorrido DUAS vezes:", list(py_list), list(py_list), "(cada for pede um iterador novo)")

# o que o for faz por baixo
it = iter(py_list)
manual = []
while True:
    try:
        manual.append(next(it))
    except StopIteration:
        break
print("o que o 'for' faz: iter() uma vez, next() até StopIteration ->", manual)


# --- 4. iterar uma árvore: o iterador precisa guardar ONDE está (a pilha explícita) ---
class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.value, self.left, self.right = value, left, right


class InOrderIterator:
    def __init__(self, root):
        self._stack = []
        self._push_left(root)

    def _push_left(self, node):
        while node is not None:
            self._stack.append(node)
            node = node.left

    def __iter__(self):
        return self

    def __next__(self):
        if not self._stack:
            raise StopIteration
        node = self._stack.pop()
        self._push_left(node.right)
        return node.value


tree = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6, TreeNode(5), TreeNode(7)))
print("\niterador em-ordem de uma árvore (estado explícito: uma pilha):", list(InOrderIterator(tree)))


# --- 5. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree_ = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree_))}


print("\nIterator (interface) + LinkedListIterator + coleção:", measure([Iterator, LinkedListIterator, LinkedList]))
print("em-ordem como classe:", measure([InOrderIterator]), "(no próximo exemplo: a mesma travessia em 6 linhas com `yield`)")


def best(fn, n=200_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


big = PyLinkedList(*range(100))
print(f"\npercorrer 100 nós com o iterador-classe: {best(lambda: sum(1 for _ in big), 5_000):.1f} µs")
