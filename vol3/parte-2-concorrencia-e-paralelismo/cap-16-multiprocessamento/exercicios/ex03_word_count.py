"""Exercício 3: contagem de palavras em paralelo (map + reduce)."""
import collections  # noqa: F401


def merge_counts(counters):
    """Soma uma sequência de ``Counter`` em um novo ``Counter`` (sem alterar os de
    entrada). Sequência vazia devolve ``Counter()``."""
    raise NotImplementedError


def parallel_word_count(texts, processes=2):
    """Conta as palavras (minúsculas, separadas por espaço) de todos os ``texts``.
    Cada texto é contado em um processo por ``tasks.count_words`` (módulo
    ``tasks``, já importável) e os resultados parciais são combinados com
    ``merge_counts``. ``texts`` vazio devolve ``Counter()`` sem criar processos."""
    raise NotImplementedError
