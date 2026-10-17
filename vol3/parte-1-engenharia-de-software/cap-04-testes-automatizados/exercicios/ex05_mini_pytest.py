"""Exercício 5: um mini executor de testes (para entender o que o pytest faz)."""
import re


class raises:
    """Gerenciador de contexto como ``pytest.raises``.

    ``with raises(ValueError, match="x") as info: ...``

    * se o bloco levantar ``exc_type`` (ou subclasse) e, quando ``match`` for
      dado, ``re.search(match, str(exceção))`` casar: engole a exceção e guarda
      em ``info.value``;
    * se não levantar nada: ``AssertionError("DID NOT RAISE <nome>")``;
    * se o texto não casar: ``AssertionError``;
    * exceção de OUTRO tipo propaga.
    """

    def __init__(self, exc_type, match=None):
        raise NotImplementedError


def parametrize(argnames, values):
    """Decorador: ``@parametrize("a, b", [(1, 2), (3, 4)])`` marca a função para
    rodar uma vez por item de ``values`` (cada item é uma tupla com um valor por
    nome; com UM nome só, o item é o próprio valor). Guarde o necessário em um
    atributo da função e devolva a mesma função."""
    raise NotImplementedError


def run_tests(module):
    """Roda os testes de ``module`` (qualquer objeto com atributos; use
    ``vars(module)``): funções chamáveis cujo nome começa com ``test_``, na
    ordem de definição.

    Devolve um dict ``{id: status}``; ``id`` é o nome da função, ou
    ``"nome[i]"`` (``i`` = índice do caso, de 0) para parametrizadas.
    ``status``: ``"passed"``, ``"failed"`` (``AssertionError``) ou ``"error"``
    (qualquer outra exceção). Funções parametrizadas recebem os valores como
    argumentos nomeados."""
    raise NotImplementedError


def summary(results):
    """``{"a": "passed", "b": "failed", "c": "error", "d": "passed"}`` ->
    ``"2 passed, 1 failed, 1 error"`` (sempre nesta ordem, só com o que for
    maior que zero; nada rodou: ``"no tests ran"``)."""
    raise NotImplementedError
