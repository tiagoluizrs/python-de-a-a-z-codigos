"""Exercício 3: __getitem__ com índices e fatias."""


class Playlist:
    """Lista de músicas.

    * ``len(p)``;
    * ``p[i]`` devolve a música (``IndexError`` se fora do limite, como a
      lista); índices negativos funcionam;
    * ``p[a:b:c]`` devolve OUTRA ``Playlist`` (e não uma lista);
    * ``reversed(p)`` e iteração funcionam;
    * ``repr`` no formato ``Playlist(['a', 'b'])``;
    * ``p[1.5]`` (tipo inválido) levanta ``TypeError``.
    """

    def __init__(self, songs):
        raise NotImplementedError
