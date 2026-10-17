"""Exercício 3: comparar modelos de execução na MESMA tarefa."""
import concurrent.futures as cf  # noqa: F401
import time  # noqa: F401


def compare_models(func, items, workers=4, models=("sequential", "threads", "processes")):
    """Executa ``func`` sobre cada item de ``items`` em cada modelo de ``models`` e
    devolve um dict ``{modelo: {"seconds": float, "results": lista}}``.

    Modelos: ``"sequential"`` (laço), ``"threads"`` (``ThreadPoolExecutor``),
    ``"processes"`` (``ProcessPoolExecutor``), cada pool com ``workers``. ``func``
    deve ser um callable de módulo (picklable). Modelo desconhecido levanta
    ``ValueError`` ANTES de executar qualquer coisa. Os ``results`` mantêm a ORDEM
    de ``items`` em todos os modelos."""
    raise NotImplementedError


def speedups(report, baseline="sequential"):
    """De um dict como o de ``compare_models``, devolve ``{modelo: ganho}`` onde
    ``ganho = seconds[baseline] / seconds[modelo]`` (sem o próprio baseline)."""
    raise NotImplementedError


def results_agree(report):
    """``True`` se todos os modelos devolveram os MESMOS resultados."""
    raise NotImplementedError
