"""Exercício 2: o Bridge com FUNÇÕES: exportadores (abstração) que escrevem por um ``write(linha)`` qualquer (implementação)."""


class CsvExporter:
    """``CsvExporter(write, delimiter=",")``: ``export(rows)`` (``rows`` é uma lista de dicts) chama ``write(linha)`` para o cabeçalho (as chaves da primeira
    linha, na ordem) e depois uma vez por registro, SEM ``\\n`` no fim das linhas. Valores viram ``str``; um campo que contenha o delimitador, aspas ou
    quebra de linha vai entre aspas duplas, com as aspas internas dobradas (como o módulo ``csv``). ``rows`` vazio: ``ValueError("sem linhas")``; uma linha
    sem uma coluna do cabeçalho: ``KeyError(coluna)``."""

    def __init__(self, write, delimiter: str = ","):
        raise NotImplementedError

    def export(self, rows: list[dict]) -> None:
        raise NotImplementedError


class JsonLinesExporter:
    """``JsonLinesExporter(write)``: ``export(rows)`` chama ``write(json.dumps(linha, ensure_ascii=False, sort_keys=True))`` por registro (sem cabeçalho).
    ``rows`` vazio: ``ValueError("sem linhas")``."""

    def __init__(self, write):
        raise NotImplementedError

    def export(self, rows: list[dict]) -> None:
        raise NotImplementedError


class TableExporter:
    """``TableExporter(write)``: ``export(rows)`` escreve uma tabela de texto, uma linha por ``write``: o cabeçalho, uma linha de separação e os registros;
    as colunas têm a largura do maior valor (cabeçalho incluído), os valores são alinhados à ESQUERDA, separados por ``" | "``, e cada linha é escrita com
    ``rstrip()`` (sem espaços no fim); a separação usa ``"-"`` por coluna, juntos por ``"-+-"``. ``rows`` vazio: ``ValueError("sem linhas")``."""

    def __init__(self, write):
        raise NotImplementedError

    def export(self, rows: list[dict]) -> None:
        raise NotImplementedError


def list_writer(target: list):
    """Devolve ``write(linha)`` que acrescenta a linha a ``target``."""
    raise NotImplementedError


def prefixed(write, prefix: str):
    """Devolve ``write2(linha)`` que chama ``write(prefix + linha)``."""
    raise NotImplementedError


def fan_out(*writers):
    """Devolve ``write(linha)`` que chama TODOS os ``writers``, na ordem. Se um deles levantar exceção, os seguintes AINDA são chamados e, no fim, a PRIMEIRA
    exceção é levantada. Sem ``writers``: ``ValueError("nenhum destino")``."""
    raise NotImplementedError


class FileWriter:
    """``FileWriter(path)``: abre ``path`` para escrita (``encoding="utf-8"``, ``newline="\\n"``) e é CHAMÁVEL: ``writer(linha)`` escreve ``linha + "\\n"``.
    Funciona como gerenciador de contexto (``with``): ao sair, fecha o arquivo; ``close()`` também fecha (e pode ser chamado duas vezes). Escrever depois de
    fechado: ``ValueError("destino fechado")``."""

    def __init__(self, path):
        raise NotImplementedError

    def __call__(self, line: str) -> None:
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, *exc):
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError
