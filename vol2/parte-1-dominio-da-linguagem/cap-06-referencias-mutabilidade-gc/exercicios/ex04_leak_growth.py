"""Exercício 4: medir vazamento com tracemalloc."""
from collections.abc import Callable


def leak_growth(func: Callable[[], None], rounds: int = 200) -> int:
    """Devolva quantos bytes ficaram retidos após chamar ``func`` ``rounds`` vezes.

    Passos sugeridos:
    1. chame ``func()`` uma vez para aquecer (caches internos, imports);
    2. ``gc.collect()``; ``tracemalloc.start()``; tire o snapshot ``before``;
    3. chame ``func()`` ``rounds`` vezes;
    4. ``gc.collect()``; tire o snapshot ``after``; pare o tracemalloc;
    5. some ``size_diff`` de ``after.compare_to(before, "filename")``
       (use apenas as diferenças positivas).

    Uma função sem vazamento deve devolver um valor pequeno (poucos KiB);
    uma que acumula 1 KiB por chamada deve devolver bem mais que
    ``rounds`` KiB.
    """
    raise NotImplementedError
