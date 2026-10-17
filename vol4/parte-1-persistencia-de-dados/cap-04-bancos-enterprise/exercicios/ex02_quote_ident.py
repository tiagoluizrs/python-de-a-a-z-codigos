"""Exercício 2: aspas de identificadores por dialeto."""


def quote_ident(dialect, name):
    """Cita ``name`` como identificador SQL do ``dialect``:

    * ``sqlite``, ``postgresql``, ``oracle``: aspas duplas, dobrando as internas (``a"b`` -> ``"a""b"``);
    * ``mysql``, ``mariadb``: crases, dobrando as internas;
    * ``mssql``: colchetes, dobrando o ``]`` (``a]b`` -> ``[a]]b]``);
    * ``name`` vazio, com ``\\x00`` ou maior que 128 caracteres levanta ``ValueError``
      (``oracle``: máximo 128 também); dialeto desconhecido levanta ``ValueError``."""
    raise NotImplementedError
