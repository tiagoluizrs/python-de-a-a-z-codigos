"""Exercício 3: tokenizador com grupos nomeados."""


def tokenize(source: str) -> list[tuple[str, str]]:
    """Quebre ``source`` em tokens ``(tipo, texto)``.

    Tipos: ``NUMBER`` (inteiro ou decimal com ponto), ``IDENT``
    (letra ou ``_`` seguida de letras, dígitos ou ``_``), ``OP`` (um
    entre ``+ - * / =``), ``LPAREN`` e ``RPAREN``. Espaços são
    descartados. Qualquer outro caractere levanta ``ValueError`` cuja
    mensagem contém a posição (índice) do caractere.

    Exemplo::

        tokenize("x = 2.5*y")
        == [("IDENT", "x"), ("OP", "="), ("NUMBER", "2.5"),
            ("OP", "*"), ("IDENT", "y")]

    Dicas: ``finditer``, ``Match.lastgroup`` e uma alternativa final
    que captura "qualquer outro caractere".
    """
    raise NotImplementedError
