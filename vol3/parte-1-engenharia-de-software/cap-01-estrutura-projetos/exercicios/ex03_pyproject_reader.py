"""Exercício 3: ler o pyproject.toml."""


def read_project(path):
    """Lê o ``pyproject.toml`` em ``path`` (``str`` ou ``Path``) com ``tomllib``
    e devolve um ``dict`` com:

    * ``name``, ``version`` (``None`` se ausente), ``requires_python`` (``None``
      se ausente);
    * ``dependencies``: lista (``[]`` se ausente);
    * ``scripts``: dict (``{}`` se ausente);
    * ``build_backend``: de ``[build-system]`` (``None`` se ausente);
    * ``groups``: dict ``{nome_do_grupo: lista}`` de ``[dependency-groups]``
      (``{}`` se ausente).

    Sem a tabela ``[project]`` ou sem ``name``, levanta ``ValueError``.
    """
    raise NotImplementedError
