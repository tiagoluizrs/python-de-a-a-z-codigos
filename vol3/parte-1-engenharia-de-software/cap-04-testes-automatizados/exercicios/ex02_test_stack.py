"""Exercício 2: escreva testes para ``Stack`` e ``EmptyStackError``.

Contrato (``alvos/stack/correto.py``): ``push(item)``, ``pop()`` remove e devolve
o ÚLTIMO empilhado, ``peek()`` devolve o último SEM remover, ``len(pilha)``,
``is_empty()``; ``pop``/``peek`` em pilha vazia levantam ``EmptyStackError``.

Seus testes precisam PASSAR no correto e FALHAR em cada um dos 7 mutantes.
"""
import pytest
from stack_impl import EmptyStackError, Stack


def test_pilha_nova_esta_vazia():
    assert Stack().is_empty()

# escreva os demais testes abaixo
