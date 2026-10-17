"""Exercício 1: duas famílias de renderização (HTML e Markdown) como dataclass de funções."""
import html
from collections.abc import Callable
from dataclasses import dataclass


def html_heading(text: str, level: int) -> str:
    """``<h{level}>texto</h{level}>`` com o texto escapado por ``html.escape``. ``level`` fora de 1 a 6: ``ValueError("nível inválido: ...")``."""
    raise NotImplementedError


def html_table(header: list, rows: list) -> str:
    """``<table><tr><th>a</th><th>b</th></tr><tr><td>1</td><td>2</td></tr></table>`` (cada célula convertida com ``str`` e escapada).
    Uma linha com número de células diferente do cabeçalho: ``ValueError("linha 2 tem 1 colunas, esperado 2")`` (a linha é contada a partir de 1)."""
    raise NotImplementedError


def html_link(text: str, url: str) -> str:
    """``<a href="url">texto</a>``, com ``url`` e texto escapados (``html.escape``, que também escapa aspas)."""
    raise NotImplementedError


def md_heading(text: str, level: int) -> str:
    """``"#" * level + " " + texto``; mesmo ``ValueError`` de nível inválido."""
    raise NotImplementedError


def md_table(header: list, rows: list) -> str:
    """Linhas ``| a | b |``, depois ``| --- | --- |``, depois as linhas, separadas por ``\\n``; mesmo ``ValueError`` de linhas desiguais."""
    raise NotImplementedError


def md_link(text: str, url: str) -> str:
    """``[texto](url)``."""
    raise NotImplementedError


@dataclass(frozen=True)
class Renderer:
    """A família: três funções (``heading``, ``table``, ``link``) que andam juntas. Complete os campos."""


RENDERERS: dict = {}     # "html" e "markdown"


def make_renderer(name: str):
    """O renderer da família (sem diferenciar maiúsculas de minúsculas). Desconhecido: ``ValueError(f"família desconhecida: {name!r}; disponíveis: html, markdown")``
    (a lista em ordem alfabética, vinda de ``RENDERERS``)."""
    raise NotImplementedError


def render_report(renderer, title: str, header: list, rows: list, url: str) -> str:
    """Título (nível 1), tabela e um link de texto ``"detalhes"``, nessa ordem, separados por uma linha em branco (``"\\n\\n"``)."""
    raise NotImplementedError
