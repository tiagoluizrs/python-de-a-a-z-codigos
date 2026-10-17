"""Exercício 4: medir memória com tracemalloc."""
import tracemalloc


def measure_peak(func, *args, **kwargs):
    """Executa ``func`` com ``tracemalloc`` e devolve ``(resultado, pico_em_bytes)``.
    Se o ``tracemalloc`` JÁ estava ativo ao chamar, respeite isso: não o pare no
    final (e meça o pico daquela chamada com ``reset_peak``)."""
    raise NotImplementedError


def top_allocations(func, *args, limit=3, **kwargs):
    """Executa ``func``, tira um instantâneo e devolve até ``limit`` pares
    ``(arquivo_sem_pasta:linha, tamanho_em_bytes)`` dos maiores alocadores
    (agrupados por linha), ordenados do maior para o menor. Ignore alocações do
    próprio módulo ``tracemalloc``. O ``arquivo_sem_pasta`` é só o nome do
    arquivo (``os.path.basename``)."""
    raise NotImplementedError


def retains_memory(func, iterations=50, tolerance=2_000):
    """``True`` se chamar ``func`` ``iterations`` vezes FAZ a memória retida
    crescer mais que ``tolerance`` bytes por iteração em média (um vazamento).
    Meça a memória atual (``get_traced_memory()[0]``) antes e depois do laço,
    com ``gc.collect()`` antes de medir."""
    raise NotImplementedError
