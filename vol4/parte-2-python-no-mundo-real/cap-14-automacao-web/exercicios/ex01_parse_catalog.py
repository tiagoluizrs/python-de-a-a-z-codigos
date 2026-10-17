"""Exercício 1: transformar o HTML de um catálogo em dados tipados."""


def parse_products(html: str) -> list[dict]:
    """``html`` é uma página de catálogo como a de ``/catalog`` do ``demo_site.py``: cada produto é um
    ``<article class="product" data-id="N">`` com ``.name``, ``.price`` (texto como ``R$ 1.299,00``; o atributo
    ``content`` de ``[itemprop=price]`` traz o número puro quando existe), ``.category`` e ``.stock``.

    Devolve uma lista de dicts, na ordem da página, com as chaves:

    * ``id`` (``int``, do ``data-id``) e ``name`` (``str``, sem espaços nas pontas);
    * ``price`` (``float``): o ``content`` de ``[itemprop=price]`` se existir; senão, o texto (``R$ 1.299,00`` ->
      ``1299.0``);
    * ``category`` (``str``; ``None`` se o elemento não existir);
    * ``stock`` (``int``): o número do texto (``"12 em estoque"`` -> ``12``) e ``0`` para ``"Esgotado"``;
      ``None`` se o elemento não existir;
    * ``in_stock`` (``bool``): ``stock`` maior que zero (``False`` quando ``stock`` for ``None``).

    Se a página não tiver nenhum ``article.product``, levante ``ValueError("layout mudou")``. Pode usar
    BeautifulSoup (``lxml``) ou selectolax."""
    raise NotImplementedError
