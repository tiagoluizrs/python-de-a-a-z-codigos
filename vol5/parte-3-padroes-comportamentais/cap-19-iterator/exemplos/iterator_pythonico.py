"""Iterator em Python: o protocolo está na linguagem; o gerador (yield) escreve o iterador por você, e as ferramentas de itertools o compõem."""
import ast
import inspect
import io
import itertools
import textwrap
import time
import tracemalloc


# --- 1. o gerador: uma função com yield É um iterador (o estado vive nas variáveis locais) ---
class LinkedNode:
    def __init__(self, value, next_node=None):
        self.value, self.next = value, next_node


class LinkedList:
    def __init__(self, *values):
        self.head = None
        for value in reversed(values):
            self.head = LinkedNode(value, self.head)

    def __iter__(self):                                       # o __iter__ É um gerador: 4 linhas, sem classe iteradora
        node = self.head
        while node is not None:
            yield node.value
            node = node.next


class TreeNode:
    def __init__(self, value, left=None, right=None):
        self.value, self.left, self.right = value, left, right

    def inorder(self):                                        # a travessia em-ordem: o estado é a PILHA DE CHAMADAS do próprio Python
        if self.left:
            yield from self.left.inorder()
        yield self.value
        if self.right:
            yield from self.right.inorder()


ll = LinkedList(10, 20, 30)
tree = TreeNode(4, TreeNode(2, TreeNode(1), TreeNode(3)), TreeNode(6, TreeNode(5), TreeNode(7)))
print("lista ligada com __iter__ gerador:", list(ll), "| duas vezes:", list(ll) == list(ll))
print("árvore em-ordem com yield from:", list(tree.inorder()))

# --- 2. preguiça: um pipeline que processa UM item por vez, sem montar listas intermediárias ---
def read_lines(text):
    for line in io.StringIO(text):
        yield line.rstrip("\n")


def only_errors(lines):
    return (line for line in lines if line.startswith("ERROR"))             # expressão geradora


def messages(lines):
    return (line.split(": ", 1)[1] for line in lines)


log = "INFO: ok\nERROR: disco cheio\nINFO: ok\nERROR: sem rede\nERROR: timeout\n"
print("\npipeline preguiçoso:", list(messages(only_errors(read_lines(log)))), "| nada foi calculado até o list()")
first = next(messages(only_errors(read_lines(log))))
print("só o primeiro erro (o resto nem é lido):", first)

# --- 3. o ganho de memória, medido ---
N = 1_000_000


def peak(fn):
    tracemalloc.start()
    result = fn()
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, peak_bytes


total_list, peak_list = peak(lambda: sum([i * 2 for i in range(N)]))
total_gen, peak_gen = peak(lambda: sum(i * 2 for i in range(N)))
print(f"\nsoma de {N:,} números: lista {peak_list / 1e6:7.1f} MB de pico | gerador {peak_gen / 1e3:7.1f} KB de pico | mesmo resultado: {total_list == total_gen}")

# --- 4. as pegadinhas: um iterador acaba, e é de UMA passada ---
gen = (x * x for x in range(3))
print("\nprimeira passada:", list(gen), "| segunda passada:", list(gen), "(um gerador esgota: a segunda vem vazia)")
iterable_range = range(3)
print("range é ITERÁVEL, não iterador:", list(iterable_range), list(iterable_range), "| iter(range) is range?", iter(iterable_range) is iterable_range)
print("lista é iterável; iter(lista) é um iterador:", iter([1, 2]) is not [1, 2], "| iter(iterador) devolve ele mesmo:", (lambda i: iter(i) is i)(iter([1])))

items = [1, 2, 3, 4]
seen = []
for x in items:
    seen.append(x)
    if x == 2:
        items.remove(2)                                          # alterar a lista DURANTE o for embaralha o percurso
print("remover durante o for pula elementos:", seen, "(o 3 foi pulado)")

# --- 5. itertools: os iteradores prontos ---
print("\nitertools:")
print("  islice(itertools.count(10), 3) :", list(itertools.islice(itertools.count(10), 3)), "(count é infinito; o islice corta)")
print("  chain([1, 2], 'ab')            :", list(itertools.chain([1, 2], "ab")))
print("  batched(range(7), 3)           :", list(itertools.batched(range(7), 3)))
print("  pairwise('abcd')               :", list(itertools.pairwise("abcd")))
print("  groupby (ordenado)             :", [(k, list(g)) for k, g in itertools.groupby(sorted("aabbbca"))])
print("  accumulate([1, 2, 3, 4])       :", list(itertools.accumulate([1, 2, 3, 4])))
stream = io.BytesIO(b"abcdefg")
print("  iter(callable, sentinela)      :", list(iter(lambda: stream.read(3), b"")))

# --- 6. send(): o gerador também RECEBE valores (corrotina simples) ---
def running_average():
    total, count, average = 0.0, 0, None
    while True:
        value = yield average
        total += value
        count += 1
        average = total / count


avg = running_average()
next(avg)
print("\ngerador com send():", [avg.send(v) for v in (10, 20, 60)])


# --- 7. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree_ = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree_))}


print("\nLinkedList.__iter__ gerador:", measure([LinkedList.__iter__]), "| árvore em-ordem:", measure([TreeNode.inorder]))


def best(fn, n=3_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


big = LinkedList(*range(100))
numbers = list(range(100))
print(f"percorrer 100 elementos: gerador {best(lambda: sum(1 for _ in big)):6.1f} µs | lista (iterador nativo em C) {best(lambda: sum(1 for _ in numbers)):6.1f} µs")
