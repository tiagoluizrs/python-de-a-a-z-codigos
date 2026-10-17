"""Abstract Factory, forma clássica (GoF): uma interface para criar FAMÍLIAS de produtos que precisam combinar entre si."""
import ast
import html
import inspect
import textwrap
import time
from abc import ABC, abstractmethod


# --- 1. os produtos: três interfaces, duas famílias (HTML e Markdown) ---
class Heading(ABC):
    @abstractmethod
    def render(self, text: str, level: int) -> str: ...


class Table(ABC):
    @abstractmethod
    def render(self, header: list, rows: list) -> str: ...


class Link(ABC):
    @abstractmethod
    def render(self, text: str, url: str) -> str: ...


class HtmlHeading(Heading):
    def render(self, text, level):
        return f"<h{level}>{html.escape(text)}</h{level}>"


class HtmlTable(Table):
    def render(self, header, rows):
        head = "".join(f"<th>{html.escape(str(h))}</th>" for h in header)
        body = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>" for row in rows)
        return f"<table><tr>{head}</tr>{body}</table>"


class HtmlLink(Link):
    def render(self, text, url):
        return f'<a href="{html.escape(url)}">{html.escape(text)}</a>'


class MarkdownHeading(Heading):
    def render(self, text, level):
        return "#" * level + " " + text


class MarkdownTable(Table):
    def render(self, header, rows):
        lines = ["| " + " | ".join(map(str, header)) + " |", "| " + " | ".join("---" for _ in header) + " |"]
        lines += ["| " + " | ".join(map(str, row)) + " |" for row in rows]
        return "\n".join(lines)


class MarkdownLink(Link):
    def render(self, text, url):
        return f"[{text}]({url})"


# --- 2. a fábrica abstrata e uma fábrica concreta por família ---
class ReportFactory(ABC):
    @abstractmethod
    def heading(self) -> Heading: ...

    @abstractmethod
    def table(self) -> Table: ...

    @abstractmethod
    def link(self) -> Link: ...


class HtmlFactory(ReportFactory):
    def heading(self):
        return HtmlHeading()

    def table(self):
        return HtmlTable()

    def link(self):
        return HtmlLink()


class MarkdownFactory(ReportFactory):
    def heading(self):
        return MarkdownHeading()

    def table(self):
        return MarkdownTable()

    def link(self):
        return MarkdownLink()


# --- 3. o cliente: recebe UMA fábrica e só conhece as interfaces ---
def render_report(factory: ReportFactory, title, header, rows, url):
    parts = [factory.heading().render(title, 1), factory.table().render(header, rows), factory.link().render("detalhes", url)]
    return "\n\n".join(parts)


data = ("Vendas", ["item", "qtd"], [["lápis", 3], ["caneta", 5]], "https://exemplo.com/vendas?a=1&b=2")
for factory in (HtmlFactory(), MarkdownFactory()):
    print(f"--- {type(factory).__name__}")
    print(render_report(factory, *data))

# --- 4. o que a família garante: nunca sai um <table> com um título em Markdown ---
print("\ntodos os produtos vêm da MESMA fábrica: o cliente não consegue misturar famílias sem querer")
mixed = HtmlHeading().render("Vendas", 1) + "\n\n" + MarkdownTable().render(*data[1:3])
print("misturar à mão (sem a fábrica) dá um documento incoerente:\n" + mixed)


# --- 5. o custo: 3 interfaces + 6 produtos + 1 fábrica abstrata + 2 concretas ---
def measure(objects):
    source = "\n".join(inspect.getsource(o) for o in objects)
    tree = ast.parse(textwrap.dedent(source))
    lines = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]
    return {"linhas": len(lines), "classes": sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))}


print("\nforma clássica:", measure([Heading, Table, Link, HtmlHeading, HtmlTable, HtmlLink, MarkdownHeading, MarkdownTable, MarkdownLink,
                                    ReportFactory, HtmlFactory, MarkdownFactory]))


def best(fn, n=100_000):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    return (time.perf_counter() - start) / n * 1e6


f = HtmlFactory()
print(f"renderizar o relatório: {best(lambda: render_report(f, *data)):.1f} µs por chamada (3 objetos criados por chamada)")

# --- 5. a desvantagem conhecida: acrescentar um PRODUTO edita TODAS as fábricas ---
print("\nacrescentar o produto 'CodeBlock': nova interface + um produto por família + um método em ReportFactory, HtmlFactory e MarkdownFactory")
print("acrescentar uma FAMÍLIA (LaTeX) é fácil: três classes e uma fábrica; acrescentar um PRODUTO é o que dói (o eixo de mudança errado para este padrão)")
