"""Exercício 4: verificar e navegar um README."""


def anchor(heading):
    """Âncora no estilo do GitHub: minúsculas, espaços viram ``-``, remove
    pontuação (mantém letras, dígitos, ``-`` e ``_``; letras acentuadas ficam).
    ``"Instalação e Uso!"`` -> ``"instalação-e-uso"``."""
    raise NotImplementedError


def table_of_contents(markdown, max_level=3):
    """Lista Markdown com os títulos (``#``, ``##``...) até ``max_level``, ignorando o
    título de nível 1 e as linhas dentro de blocos de código (```). Cada título de
    nível ``n`` (>= 2) vira uma linha ``"  " * (n - 2) + "- [texto](#âncora)"``,
    juntas por ``"\\n"``. Âncoras repetidas ganham ``-1``, ``-2``... como no GitHub."""
    raise NotImplementedError


def check_readme(markdown):
    """Devolve a lista ORDENADA de problemas (códigos) de um README:

    * ``"no-title"``: a primeira linha não vazia não é um título ``# ...``;
    * ``"no-install"``: nenhum título contém ``instal`` ou ``install``;
    * ``"no-usage"``: nenhum título contém ``uso``, ``usage`` ou ``exemplo``;
    * ``"no-license"``: nenhum título contém ``licen``;
    * ``"no-code"``: não há bloco de código ```;
    * ``"empty-link"``: algum link ``[texto]()`` sem destino;
    * ``"too-short"``: menos de 5 linhas não vazias."""
    raise NotImplementedError
