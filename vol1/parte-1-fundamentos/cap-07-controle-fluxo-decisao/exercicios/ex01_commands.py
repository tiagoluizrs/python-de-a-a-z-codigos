"""Exercício 1: classificar comandos de um jogo de texto com match."""


def parse_command(line: str) -> tuple:
    """Classifique uma linha digitada pelo jogador.

    Regras (use ``match`` sobre ``line.split()``):

    - ``"go north"`` (north, south, east, west) -> ``("move", "north")``
    - ``"go"`` ou direção inválida -> ``("error", "go where?")``
    - ``"pick sword"`` -> ``("pick", "sword")``
    - ``"pick magic sword"`` (vários itens) -> ``("pick", "magic sword")``
    - ``"quit"`` ou ``"exit"`` -> ``("quit",)``
    - linha vazia -> ``("noop",)``
    - qualquer outra coisa -> ``("unknown", primeira_palavra)``

    Dica: padrões de sequência, OR-patterns, ``*rest`` e ``as``.
    """
    raise NotImplementedError
