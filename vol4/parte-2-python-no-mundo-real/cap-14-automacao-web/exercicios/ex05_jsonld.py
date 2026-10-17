"""Exercício 5: ler os dados estruturados (JSON-LD) que os sites escrevem para as máquinas."""


def extract_jsonld(html: str) -> list[dict]:
    """Devolve todos os objetos JSON-LD da página (``<script type="application/ld+json">``), em ordem.

    * um script pode conter um objeto, uma LISTA de objetos ou um objeto com ``"@graph"`` (uma lista): achate tudo
      em uma lista de dicts (quando houver ``@graph``, devolva os itens do grafo e NÃO o objeto que o contém);
    * script com JSON inválido ou vazio é IGNORADO (nunca levante exceção por isso);
    * elementos da lista que não forem objetos (números, textos) são ignorados."""
    raise NotImplementedError


def products_summary(html: str) -> list[dict]:
    """Dos objetos JSON-LD, os de ``@type`` ``"Product"`` (o ``@type`` pode ser uma lista que contenha ``"Product"``).
    Para cada um devolva ``{"name": ..., "sku": ..., "price": float, "currency": ..., "available": bool}``, lendo
    ``offers`` (um objeto OU uma lista: use o primeiro). ``available`` é ``True`` se ``availability`` terminar em
    ``InStock`` (``"InStock"`` ou ``"https://schema.org/InStock"``). Campo ausente vira ``None`` (e ``available``,
    ``False``); o preço pode vir como texto (``"1299.00"``)."""
    raise NotImplementedError
