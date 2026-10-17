"""Exercício 2: seguir a paginação com segurança (sem rede: quem baixa é uma função que você recebe)."""


def crawl(fetch, start_url: str, max_pages: int = 50):
    """``fetch(url)`` devolve o HTML (``str``) da URL ou ``None`` se a página não existir (404).

    Siga os links ``<a rel="next" href="...">`` a partir de ``start_url``, resolvendo cada ``href`` em relação à URL da
    página atual (``urllib.parse.urljoin``; o ``href`` pode ser relativo, como ``?page=2`` ou ``/catalog?page=2``).

    Devolve ``(urls, items)``: ``urls`` é a lista das URLs visitadas em ordem e ``items`` é a lista dos textos de
    cada ``.name`` de cada página (em ordem). Regras:

    * pare quando não houver link ``rel=next``, quando ``fetch`` devolver ``None`` (essa URL NÃO conta como visitada)
      ou quando atingir ``max_pages`` páginas;
    * NUNCA visite a mesma URL duas vezes (um site com um ``next`` que volta para trás não pode gerar laço infinito);
    * use ``fetch`` UMA vez por página."""
    raise NotImplementedError
