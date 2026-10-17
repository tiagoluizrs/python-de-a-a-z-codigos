"""Exercício 6: um profiler por amostragem de brinquedo."""
import sys
import threading
import time
from collections import Counter


def sample_profile(func, *args, interval=0.001, **kwargs):
    """Executa ``func(*args, **kwargs)`` na thread atual enquanto uma thread
    auxiliar, a cada ``interval`` segundos, olha onde a thread principal está
    (``sys._current_frames()[id_da_thread_principal]``) e conta o NOME
    (``frame.f_code.co_name``) da função em execução naquele instante (o quadro
    do TOPO da pilha).

    Devolve ``(resultado, contador)`` com ``collections.Counter`` nome -> amostras.
    A thread auxiliar deve parar (``threading.Event``) e ser aguardada
    (``join``) ao final, mesmo se ``func`` levantar exceção (que propaga)."""
    raise NotImplementedError


def hottest(counter, n=1):
    """Os ``n`` nomes mais amostrados, como lista de ``(nome, fração)`` em que
    ``fração`` é ``amostras / total`` (``float``). Contador vazio: ``[]``."""
    raise NotImplementedError
