"""Exercício 3: complexidade ciclomática."""


def cyclomatic_complexity(source):
    """Devolve ``{nome: complexidade}`` para cada função de ``source`` (texto):
    funções de módulo pelo nome, métodos como ``"Classe.metodo"``, funções
    internas como ``"externa.interna"`` (cada uma com a SUA complexidade; as
    decisões de uma função interna NÃO contam para a externa).

    Complexidade = 1 + número de: ``if`` (cada ``elif`` é um ``if``), ``for``,
    ``while``, ``except``, expressão ``a if c else b``, cada operador
    booleano extra (``a and b and c`` soma 2), cada ``for`` e cada ``if`` de
    uma compreensão ou expressão geradora, e cada ``case`` de um ``match``.
    ``async`` conta igual."""
    raise NotImplementedError


def too_complex(source, limit=10):
    """Lista ORDENADA dos nomes cuja complexidade é MAIOR que ``limit``."""
    raise NotImplementedError
