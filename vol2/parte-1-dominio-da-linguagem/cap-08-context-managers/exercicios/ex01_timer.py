"""Exercício 1: um Timer reutilizável e testável."""
import time


class Timer:
    """Context manager que mede o tempo do bloco.

    * ``Timer(clock=time.perf_counter)``: o relógio é injetável (para testes);
    * ao entrar, devolve ``self``;
    * ao sair, guarda ``elapsed`` (segundos) mesmo se o bloco levantar
      exceção, e NÃO suprime a exceção;
    * ``laps``: lista com o ``elapsed`` de cada uso (a mesma instância pode
      ser reutilizada várias vezes);
    * antes do primeiro uso, ``elapsed`` é ``None``.
    """

    def __init__(self, clock=time.perf_counter):
        raise NotImplementedError
