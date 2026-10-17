"""Exercício 3: converter placeholders ``?`` para o estilo do driver."""


def convert_placeholders(dialect, sql):
    """Recebe SQL escrito com ``?`` e devolve com o estilo do dialeto:

    * ``sqlite`` e ``mssql`` (mssql-python): ``?`` (sem mudança);
    * ``postgresql``, ``mysql``, ``mariadb``: ``%s`` (e então um ``%`` literal vira ``%%``);
    * ``oracle``: ``:1``, ``:2``, ... na ordem de aparição;
    * um ``?`` DENTRO de literal entre aspas simples (``'quem?'``, com ``''`` escapando)
      NÃO é placeholder e deve ser preservado;
    * dialeto desconhecido levanta ``ValueError``."""
    raise NotImplementedError
