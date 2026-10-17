"""Exercício 3: um ranking com conjunto ordenado."""


class Leaderboard:
    """``Leaderboard(redis, name)`` com ``redis`` criado com ``decode_responses=True``; chave ``lb:<name>``.

    * ``add(member, points)``: SOMA ``points`` (``ZINCRBY``) e devolve a nova pontuação (``float``);
    * ``score(member)`` -> pontuação ou ``None``;
    * ``rank(member)`` -> posição 1-based (1 = maior pontuação) ou ``None``; em empate, vale a ordem
      que o Redis dá para ``ZREVRANK``;
    * ``top(n)`` -> lista de ``(membro, pontuação)`` do maior para o menor (``ZREVRANGE``);
      ``n < 1`` levanta ``ValueError``;
    * ``around(member, k)`` -> até ``k`` vizinhos de cada lado (incluindo o próprio membro), em ordem
      de ranking, como lista de ``(posição, membro, pontuação)``; membro ausente levanta ``KeyError``;
    * ``remove(member)`` -> ``True`` se existia; ``size()``."""

    def __init__(self, redis, name):
        raise NotImplementedError
