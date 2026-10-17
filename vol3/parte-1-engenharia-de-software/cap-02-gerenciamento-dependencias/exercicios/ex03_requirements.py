"""Exercício 3: ler linhas de requirements."""


def normalize_name(name):
    """Normalização da PEP 503: minúsculas e sequências de ``-``, ``_`` e
    ``.`` viram um único ``-``. ``"Django_REST.framework"`` ->
    ``"django-rest-framework"``."""
    raise NotImplementedError


def parse_requirement(line):
    """Interpreta ``"Nome[extra1,extra2]>=1,<2 ; marcador"`` e devolve um dict:
    ``{"name": <normalizado>, "extras": [ordenados], "specifier": <texto sem
    espaços ou "">, "marker": <texto ou None>}``.

    Comentários (``#`` e o que vem depois) são removidos antes. Linha vazia ou
    nome inválido levanta ``ValueError``. Não use ``packaging``."""
    raise NotImplementedError


def parse_requirements(text):
    """Lê o conteúdo de um ``requirements.txt``: ignora linhas vazias,
    comentários e opções (linhas que começam com ``-``); devolve a lista de
    dicts de ``parse_requirement``, na ordem. Erro em uma linha levanta
    ``ValueError`` com o número da linha (``"linha 3: ..."``)."""
    raise NotImplementedError
