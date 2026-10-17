"""Gabarito do exercício 1."""
import re

from bs4 import BeautifulSoup


def _price(card) -> float:
    meta = card.select_one("[itemprop=price]")
    if meta is not None and meta.get("content"):
        return float(meta["content"])
    text = card.select_one(".price").get_text()
    return float(re.sub(r"[^\d,]", "", text).replace(",", "."))


def _stock(card):
    node = card.select_one(".stock")
    if node is None:
        return None
    match = re.search(r"\d+", node.get_text())
    return int(match.group()) if match else 0


def parse_products(html):
    cards = BeautifulSoup(html, "lxml").select("article.product")
    if not cards:
        raise ValueError("layout mudou")
    products = []
    for card in cards:
        category = card.select_one(".category")
        stock = _stock(card)
        products.append({
            "id": int(card["data-id"]),
            "name": card.select_one(".name").get_text(strip=True),
            "price": _price(card),
            "category": category.get_text(strip=True) if category else None,
            "stock": stock,
            "in_stock": bool(stock),
        })
    return products
