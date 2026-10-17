"""Exercício 2: um mini linter com cinco regras."""


def lint(source):
    """Devolve a lista ORDENADA de ``(linha, código)`` do texto ``source``:

    * ``"E722"``: ``except:`` sem tipo (a linha do ``except``);
    * ``"B006"``: argumento padrão mutável: literal ``[]``, ``{}`` ou
      ``{1}``, ou chamada ``list()``, ``dict()``, ``set()`` (a linha do
      valor padrão; vale também para argumentos só-nomeados);
    * ``"E711"``: comparação ``== None`` ou ``!= None``;
    * ``"E712"``: comparação ``== True/False`` ou ``!= True/False``;
    * ``"F401"``: import não usado (a linha do ``import``, uma entrada por
      NOME não usado). Um nome é usado se aparece como ``ast.Name`` em algum
      lugar (``import a.b`` define ``a``; ``import x as y`` define ``y``).
      Ignore ``from __future__ import ...`` e imports em ``__init__``-style
      reexportados por ``__all__`` (se ``__all__`` listar o nome, está usado).

    Ordene por ``(linha, código)``; repetições legítimas (dois achados
    iguais na mesma linha) aparecem repetidas."""
    raise NotImplementedError
