"""Exercício 1: contar instruções de bytecode."""


def opcode_histogram(func):
    """``Counter`` dos nomes das instruções (``dis.get_instructions``) de
    ``func``, INCLUINDO os objetos de código aninhados (funções internas,
    lambdas e classes definidas dentro dela, em ``co_consts``).

    Não conte pseudo-instruções como ``CACHE`` (o ``dis`` já as omite por
    padrão); não compare nomes exatos entre versões nos seus testes."""
    raise NotImplementedError


def count_instructions(func):
    """Total de instruções de ``func`` (incluindo as dos códigos aninhados)."""
    raise NotImplementedError


def uses_global(func, name):
    """``True`` se o bytecode de ``func`` (e dos aninhados) carrega o nome
    GLOBAL ``name`` (instruções ``LOAD_GLOBAL``); use o campo ``argval``."""
    raise NotImplementedError
