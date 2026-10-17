"""Exercício 3: prever o que o cache de camadas vai reaproveitar (e ordenar as instruções para reaproveitar mais)."""


def first_invalidated(instructions: list[tuple[str, str]], changed: set[str]) -> int | None:
    """``instructions`` é a lista de ``(tipo, argumento)`` do Dockerfile, na ordem. Só ``COPY`` depende de arquivos do
    contexto: o argumento é um texto como ``"pyproject.toml uv.lock ./"`` ou ``"src ./src"`` (todos os tokens menos o
    último são ORIGENS; o último é o destino; ignore opções que começam com ``--``). ``changed`` é o conjunto de caminhos
    que mudaram desde o último build (ex.: ``{"src/app/main.py"}``).

    Uma origem é afetada se um caminho de ``changed`` for IGUAL a ela, estiver DENTRO dela (``src/app/main.py`` dentro de
    ``src``) ou se a origem for ``.`` (tudo). Devolve o ÍNDICE da primeira instrução invalidada (a partir dela, TODAS as
    seguintes são refeitas) ou ``None`` se o cache vale inteiro. Instruções que não são ``COPY`` nunca invalidam sozinhas."""
    raise NotImplementedError


def rebuild_cost(instructions: list[tuple[str, str]], seconds: list[float], changed: set[str]) -> float:
    """Tempo estimado do build: a soma de ``seconds`` da primeira instrução invalidada até o fim (``0.0`` se nenhuma).
    ``seconds[i]`` é o custo da instrução ``i`` (mesmo tamanho de ``instructions``; senão, ``ValueError``)."""
    raise NotImplementedError


def best_order(instructions: list[tuple[str, str]], change_frequency: dict[str, float]) -> list[tuple[str, str]]:
    """Reordena as instruções de ``COPY`` consecutivas (um bloco de ``COPY`` sem ``RUN`` no meio) para que as origens que
    mudam MENOS fiquem primeiro. ``change_frequency`` dá, por origem (o primeiro token de origem do ``COPY``), a frequência de
    mudança (maior = muda mais; origem ausente: ``1.0``). Ordenação estável. Instruções que não são ``COPY`` ficam onde
    estão; apenas BLOCOS contíguos de ``COPY`` são reordenados entre si."""
    raise NotImplementedError
