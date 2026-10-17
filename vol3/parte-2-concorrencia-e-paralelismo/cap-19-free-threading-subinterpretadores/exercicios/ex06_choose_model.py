"""Exercício 6: a árvore de decisão final da Parte 2."""


def choose_model(*, cpu_bound, many_connections=False, shared_data=False, free_threaded=False, uses_pure_python=True):
    """Devolve UM de: ``"asyncio"``, ``"threads"``, ``"processes"``, ``"interpreters"``,
    ``"free-threaded threads"``.

    Regras, nesta ordem:
    1. NÃO ``cpu_bound`` (espera): ``many_connections`` -> ``"asyncio"``; senão ``"threads"``;
    2. CPU e ``free_threaded`` (o interpretador é um build sem GIL com GIL desligado)
       -> ``"free-threaded threads"``;
    3. CPU e ``shared_data`` (muito estado compartilhado) -> ``"processes"``
       (memória compartilhada explícita) quando NÃO ``uses_pure_python``; se
       ``uses_pure_python`` -> ``"interpreters"``;
    4. CPU, sem dados compartilhados e ``uses_pure_python`` -> ``"interpreters"``;
    5. CPU, sem dados compartilhados e com extensões em C -> ``"processes"``."""
    raise NotImplementedError
