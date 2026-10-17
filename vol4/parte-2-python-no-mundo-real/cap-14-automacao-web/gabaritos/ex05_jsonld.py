"""Gabarito do exercício 5."""
import json

from bs4 import BeautifulSoup


def extract_jsonld(html):
    found = []
    for script in BeautifulSoup(html, "lxml").select('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.string or "")
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("@graph"), list):
                found += [node for node in item["@graph"] if isinstance(node, dict)]
            else:
                found.append(item)
    return found


def products_summary(html):
    out = []
    for item in extract_jsonld(html):
        kind = item.get("@type")
        if kind != "Product" and not (isinstance(kind, list) and "Product" in kind):
            continue
        offers = item.get("offers")
        offer = offers[0] if isinstance(offers, list) and offers else offers if isinstance(offers, dict) else {}
        price = offer.get("price")
        availability = offer.get("availability")
        out.append({
            "name": item.get("name"),
            "sku": item.get("sku"),
            "price": float(price) if price is not None else None,
            "currency": offer.get("priceCurrency"),
            "available": isinstance(availability, str) and availability.endswith("InStock"),
        })
    return out
