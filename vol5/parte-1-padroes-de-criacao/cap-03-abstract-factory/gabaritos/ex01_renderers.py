"""Gabarito do exercício 1."""
import html
from collections.abc import Callable
from dataclasses import dataclass


def _check_level(level):
    if not 1 <= level <= 6:
        raise ValueError(f"nível inválido: {level}")


def _check_rows(header, rows):
    for i, row in enumerate(rows, 1):
        if len(row) != len(header):
            raise ValueError(f"linha {i} tem {len(row)} colunas, esperado {len(header)}")


def html_heading(text, level):
    _check_level(level)
    return f"<h{level}>{html.escape(text)}</h{level}>"


def html_table(header, rows):
    _check_rows(header, rows)
    head = "".join(f"<th>{html.escape(str(h))}</th>" for h in header)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>" for row in rows)
    return f"<table><tr>{head}</tr>{body}</table>"


def html_link(text, url):
    return f'<a href="{html.escape(url)}">{html.escape(text)}</a>'


def md_heading(text, level):
    _check_level(level)
    return "#" * level + " " + text


def md_table(header, rows):
    _check_rows(header, rows)
    lines = ["| " + " | ".join(map(str, header)) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    lines += ["| " + " | ".join(map(str, row)) + " |" for row in rows]
    return "\n".join(lines)


def md_link(text, url):
    return f"[{text}]({url})"


@dataclass(frozen=True)
class Renderer:
    heading: Callable
    table: Callable
    link: Callable


RENDERERS = {"html": Renderer(html_heading, html_table, html_link), "markdown": Renderer(md_heading, md_table, md_link)}


def make_renderer(name):
    key = name.strip().lower()
    try:
        return RENDERERS[key]
    except KeyError:
        raise ValueError(f"família desconhecida: {name!r}; disponíveis: {', '.join(sorted(RENDERERS))}") from None


def render_report(renderer, title, header, rows, url):
    return "\n\n".join([renderer.heading(title, 1), renderer.table(header, rows), renderer.link("detalhes", url)])
