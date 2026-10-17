"""Exercício 5: problemas de espaço e tamanho de linha."""


def line_issues(source, max_length=88):
    """Devolve a lista ORDENADA de ``(linha, código)`` (linhas numeradas de 1):

    * ``"W191"``: a indentação da linha começa com tabulação;
    * ``"W291"``: espaços/tabs no FIM de uma linha com conteúdo;
    * ``"W293"``: linha só de espaços/tabs (em branco, mas com espaço);
    * ``"E501"``: mais de ``max_length`` caracteres (sem contar o ``\\n``);
    * ``"W391"``: o arquivo termina com uma ou mais linhas em branco (um achado,
      na PRIMEIRA linha em branco do final);
    * ``"W292"``: o arquivo não termina com ``\\n`` (na última linha).

    Texto vazio: sem achados."""
    raise NotImplementedError
