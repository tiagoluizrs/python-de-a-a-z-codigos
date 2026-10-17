"""Exercício 2: estimar a complexidade empiricamente."""
import time


def estimate_exponent(sizes, times):
    """Inclinação da reta de mínimos quadrados de ``log(times)`` contra
    ``log(sizes)``: o ``k`` de ``tempo ~ n**k``. Precisa de pelo menos 2 pontos
    e de valores positivos; senão, ``ValueError``."""
    raise NotImplementedError


def classify(exponent):
    """``"constante"`` se ``exponent < 0.3``; ``"linear"`` se ``< 1.4``;
    ``"quadrática"`` se ``< 2.4``; ``"cúbica ou pior"`` caso contrário."""
    raise NotImplementedError


def measure_scaling(func, make_input, sizes, repeat=3, clock=time.perf_counter):
    """Para cada ``n`` em ``sizes``: gera ``make_input(n)`` (FORA da medição),
    mede ``func(entrada)`` ``repeat`` vezes com ``clock`` e guarda o MENOR tempo.
    Devolve ``(exponente_estimado, lista_de_tempos)``."""
    raise NotImplementedError
