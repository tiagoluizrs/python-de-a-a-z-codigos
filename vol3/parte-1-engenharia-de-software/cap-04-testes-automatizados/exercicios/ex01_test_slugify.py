"""Exercício 1: escreva testes para ``slugify``.

A função (``alvos/slugify/correto.py``) transforma texto em um "slug" de URL:
minúsculas, SEM acentos (``ç`` vira ``c``), só letras e dígitos separados por UM
hífen, sem hífen nas pontas; texto vazio vira ``""``.

Seus testes serão executados contra a versão correta (têm de PASSAR) e contra
7 versões com defeitos plantados, os MUTANTES (cada uma tem de FALHAR em pelo
menos um teste seu). Se algum mutante sobreviver, a correção diz qual.
"""
from slugify_impl import slugify


def test_exemplo_basico():
    assert slugify("Olá Mundo") == "ola-mundo"

# escreva os demais testes abaixo (pense em: acentos, espaços repetidos, pontas,
# maiúsculas, dígitos, texto vazio, símbolos...)
