"""Abstract Factory, forma pythônica: uma família é um conjunto de funções que andam juntas (um módulo, um dataclass, um dict)."""
import ast
import html
import inspect
import ntpath
import posixpath
import textwrap
import time
from dataclasses import dataclass
from typing import Callable


# --- 1. a família como um dataclass de funções: criar um Renderer SEM todos os produtos é um erro ---
def html_heading(text, level):
    return f"<h{level}>{html.escape(text)}</h{level}>"


def html_table(header, rows):
    head = "".join(f"<th>{html.escape(str(h))}</th>" for h in header)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><tr>{head}</tr>{body}</table>"


def html_link(text, url):
    return f'<a href="{html.escape(url)}">{html.escape(text)}</a>'


def md_heading(text, level):
    return "#" * level + " " + text


def md_table(header, rows):
    lines = ["| " + " | ".join(map(str, header)) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    lines += ["| " + " | ".join(map(str, row)) + " |" for row in rows]
    return "\n".join(lines)


def md_link(text, url):
    return f"[{text}]({url})"


@dataclass(frozen=True)
class Renderer:
    heading: Callable[[str, int], str]
    table: Callable[[list, list], str]
    link: Callable[[str, str], str]


RENDERERS = {
    "html": Renderer(html_heading, html_table, html_link),
    "markdown": Renderer(md_heading, md_table, md_link),
}


def render_report(renderer: Renderer, title, header, rows, url):
    return "\n\n".join([renderer.heading(title, 1), renderer.table(header, rows), renderer.link("detalhes", url)])


data = ("Vendas", ["item", "qtd"], [["lápis", 3], ["caneta", 5]], "https://exemplo.com/vendas?a=1&b=2")
for name, renderer in RENDERERS.items():
    print(f"--- {name}")
    print(render_report(renderer, *data))

try:
    Renderer(html_heading, html_table)                                  # type: ignore[call-arg]
except TypeError as error:
    print("\numa família incompleta falha na criação:", error)

# --- 2. o mesmo resultado que a forma clássica, sem uma classe de produto ---
print("\nacrescentar uma família (LaTeX): três funções e uma linha em RENDERERS; acrescentar um produto: um campo no dataclass")
print("(o verificador de tipos e o TypeError da criação apontam TODAS as famílias que ainda não o têm)")

# --- 3. a biblioteca padrão já é uma fábrica abstrata: os módulos posixpath e ntpath ---
print("\nmódulos como famílias (os mesmos nomes, comportamentos diferentes):")
for family in (posixpath, ntpath):
    print(f"  {family.__name__:<9} sep={family.sep!r:<5} join('a', 'b')={family.join('a', 'b')!r:<8} splitdrive('C:/x')={family.splitdrive('C:/x')}")
print("os.path é, em cada sistema, UM desses dois módulos (os.path is posixpath no Linux; os.path is ntpath no Windows)")

# --- 4. o custo ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nforma pythônica:", measure([html_heading, html_table, html_link, md_heading, md_table, md_link, Renderer]))


def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


r = RENDERERS["html"]
print(f"renderizar o relatório: {best(lambda: render_report(r, *data)):.1f} µs por chamada")

# --- 5. quando as classes continuam fazendo sentido: os produtos têm ESTADO e vários métodos (um conjunto de widgets, um driver de banco) ---
print("\nquando manter objetos: se cada produto tem estado e vários métodos (uma conexão, um cursor, um tradutor de SQL) e os três precisam ser do mesmo driver,")
print("a fábrica abstrata clássica (ou um Protocol por produto) deixa de ser cerimônia: o contrato é maior que uma função")
