"""Exercício 3: perfil determinístico com cProfile."""
import cProfile
import pstats


def profile_function(func, *args, top=5, **kwargs):
    """Executa ``func(*args, **kwargs)`` sob ``cProfile`` e devolve
    ``(resultado, linhas)``, onde ``linhas`` é uma lista de até ``top`` tuplas
    ``(nome, chamadas, tempo_próprio)`` ordenadas por tempo próprio decrescente.

    ``nome`` é só o NOME da função (o 3º item da chave ``(arquivo, linha,
    nome)`` de ``pstats.Stats(profile).stats``), ``chamadas`` o número TOTAL de
    chamadas (``ncalls``, incluindo as recursivas) e ``tempo_próprio`` o
    ``tottime``. Use ``profile.runcall(func, ...)``."""
    raise NotImplementedError


def call_counts(func, *args, **kwargs):
    """``{nome: chamadas}`` das funções DEFINIDAS EM PYTHON (ignore as embutidas,
    isto é, as com ``arquivo`` começando por ``"~"``) executadas por
    ``func(*args, **kwargs)``, incluindo a própria ``func``."""
    raise NotImplementedError
