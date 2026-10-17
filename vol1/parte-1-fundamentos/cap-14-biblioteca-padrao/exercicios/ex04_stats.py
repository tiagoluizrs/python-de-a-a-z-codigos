"""Exercício 4: estatísticas de um texto com statistics e Counter."""


def text_stats(text: str) -> dict:
    """Devolva um dicionário com:

    - ``"words"``: número de palavras (``text.lower().split()``);
    - ``"unique"``: número de palavras distintas;
    - ``"mean_len"``: tamanho médio das palavras, arredondado a 2 casas
      (``statistics.fmean``);
    - ``"median_len"``: mediana dos tamanhos (``statistics.median``);
    - ``"top"``: lista das 2 palavras mais comuns como ``(palavra, n)``
      (``Counter.most_common``). Empates seguem a ordem de 1a aparição.

    Texto sem palavras: ``{"words": 0, "unique": 0, "mean_len": 0.0,
    "median_len": 0, "top": []}``. Não deixe ``StatisticsError`` escapar.
    """
    raise NotImplementedError
