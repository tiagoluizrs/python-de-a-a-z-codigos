"""Exercício 3: o problema do N+1: medir quantas consultas o seu código faz e trocar "uma por autor" por 2 (``IN``) ou 1 (``JOIN``)."""
import sqlite3

CHUNK = 500                                                     # (Pronto.) quantos ids vão em cada ``IN (...)``: o sqlite limita o número de parâmetros de uma consulta

# Esquema (criado pelos testes):
#   authors(id INTEGER PRIMARY KEY, name TEXT UNIQUE)
#   books(id INTEGER PRIMARY KEY, author_id INTEGER, title TEXT)


class QueryCounter:
    """Um gerenciador de contexto que CONTA as consultas ``SELECT`` feitas em uma conexão: ``with QueryCounter(conn) as q: ...``.

    * ``__enter__``: instala um *trace callback* na conexão (``conn.set_trace_callback``) e devolve ``self``;
    * ``count``: quantas instruções que começam com ``SELECT`` (sem diferenciar maiúsculas e ignorando espaços iniciais) foram executadas DENTRO do ``with``; ``statements``: a lista delas;
    * ``__exit__``: remove o *trace callback* (``set_trace_callback(None)``), mesmo se houve exceção, e devolve ``False``;
    * usar um ``QueryCounter`` de novo começa do zero."""

    def __init__(self, conn: sqlite3.Connection):
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError

    @property
    def count(self) -> int:
        raise NotImplementedError

    @property
    def statements(self) -> list[str]:
        raise NotImplementedError


def titles_naive(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """``{nome_do_autor: [títulos...]}`` com o N+1: UMA consulta para os autores (``ORDER BY name``) e UMA consulta por autor para os livros (``WHERE author_id = ? ORDER BY title``).
    Autor sem livros: lista vazia. A ordem do dicionário é a dos nomes."""
    raise NotImplementedError


def titles_in(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """O mesmo resultado com poucas consultas: UMA para os autores e, para os livros, UMA por lote de ``CHUNK`` autores, com ``WHERE author_id IN (?, ?, ...)``
    (tantos ``?`` quantos os ids do lote; ``ORDER BY title``). Sem autores: só a consulta dos autores (nenhuma de livros)."""
    raise NotImplementedError


def titles_join(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """O mesmo resultado com UMA consulta: ``authors LEFT JOIN books`` (``ORDER BY authors.name, books.title``); o autor sem livros aparece com lista vazia (cuidado com o ``None`` que o
    ``LEFT JOIN`` devolve no título)."""
    raise NotImplementedError
