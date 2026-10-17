"""Exercício 4: o Builder do GoF: o MESMO processo (o diretor) montando representações DIFERENTES."""


class TextBuilder:
    """``title(texto)``, ``row(nome, valor)`` e ``result() -> str``. Formato: o título em MAIÚSCULAS, depois uma linha ``- nome: valor`` por registro,
    tudo separado por ``\\n``."""

    def title(self, text: str) -> None:
        raise NotImplementedError

    def row(self, name: str, value) -> None:
        raise NotImplementedError

    def result(self) -> str:
        raise NotImplementedError


class MarkdownBuilder:
    """Mesma interface. Formato: ``# Título`` (como veio), uma linha em branco e as linhas ``- **nome**: valor``, separadas por ``\\n``
    (sem registros, só o título)."""

    def title(self, text: str) -> None:
        raise NotImplementedError

    def row(self, name: str, value) -> None:
        raise NotImplementedError

    def result(self) -> str:
        raise NotImplementedError


class CsvBuilder:
    """Mesma interface. O ``title`` é IGNORADO. Formato: ``nome,valor`` na primeira linha e uma linha ``nome,valor`` por registro (valores com
    vírgula ou aspas vão entre aspas duplas, aspas dobradas: use o módulo ``csv`` com ``lineterminator="\\n"``), separadas por ``\\n``, com
    ``\\n`` no fim."""

    def title(self, text: str) -> None:
        raise NotImplementedError

    def row(self, name: str, value) -> None:
        raise NotImplementedError

    def result(self) -> str:
        raise NotImplementedError


def build_report(builder, title: str, rows: list[tuple]) -> str:
    """O DIRETOR: chama ``builder.title(title)``, depois ``builder.row(nome, valor)`` para cada ``(nome, valor)`` de ``rows``, e devolve
    ``builder.result()``. ``title`` vazio: ``ValueError("título obrigatório")``. NÃO conhece nenhuma classe concreta."""
    raise NotImplementedError


def build_all(builders: dict, title: str, rows: list[tuple]) -> dict[str, str]:
    """Aplica ``build_report`` a CADA builder de ``builders`` (``{nome: builder}``) e devolve ``{nome: resultado}`` na mesma ordem."""
    raise NotImplementedError
