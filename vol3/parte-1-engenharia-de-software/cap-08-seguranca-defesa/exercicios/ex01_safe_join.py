"""Exercício 1: juntar caminhos com nomes vindos de fora, sem sair da pasta-base."""
from pathlib import Path


def safe_join(base, *parts):
    """Devolve o caminho RESOLVIDO (``Path``) de ``base`` + ``parts``, garantindo
    que ele fica DENTRO de ``base``.

    Levante ``ValueError`` se: alguma parte for absoluta (inclusive ``/x`` e,
    no Windows, ``C:/x``), contiver byte nulo (``"\\0"``), ou o resultado
    resolvido sair da base (``..``, ``a/../../x``). ``a/../b`` que continua
    dentro é aceito. Sem partes, devolve a base resolvida. A base não precisa
    existir."""
    raise NotImplementedError
