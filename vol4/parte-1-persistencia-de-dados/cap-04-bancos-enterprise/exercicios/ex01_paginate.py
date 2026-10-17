"""Exercício 1: paginação por dialeto."""

DIALECTS = ("sqlite", "postgresql", "mysql", "mariadb", "oracle", "mssql")


def paginate(dialect, sql, limit, offset=0):
    """Devolve ``sql`` com a paginação do ``dialect``, com ``limit`` e ``offset`` NO TEXTO
    (inteiros validados: ``limit >= 1``, ``offset >= 0``, senão ``ValueError``).

    * ``sqlite``, ``postgresql``, ``mysql``, ``mariadb``: ``<sql> LIMIT <limit> OFFSET <offset>``;
    * ``oracle`` (12c+) e ``mssql``: ``<sql> OFFSET <offset> ROWS FETCH NEXT <limit> ROWS ONLY``;
      no ``mssql`` e no ``oracle`` o ``sql`` PRECISA ter ``ORDER BY`` (sem diferenciar
      maiúsculas), senão ``ValueError``;
    * ``sql`` pode terminar com ``;`` e/ou espaços: remova-os antes de acrescentar;
    * dialeto desconhecido levanta ``ValueError``."""
    raise NotImplementedError
