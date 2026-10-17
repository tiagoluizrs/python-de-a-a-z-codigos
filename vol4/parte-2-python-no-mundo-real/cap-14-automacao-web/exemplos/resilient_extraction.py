"""Extração que sobrevive: validar o que sai do HTML, detectar mudanças de layout e testar com páginas salvas."""
import re
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError, field_validator

import demo_site

server, BASE = demo_site.start()
FIXTURES = Path(__file__).parent / "saida" / "paginas"
FIXTURES.mkdir(parents=True, exist_ok=True)


# 1. o Pydantic do Capítulo 10 na fronteira: o que sai do HTML é "texto de qualquer coisa"
class Product(BaseModel):
    id: int
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    in_stock: bool

    @field_validator("price", mode="before")
    @classmethod
    def parse_brl(cls, value):
        if isinstance(value, str):
            return float(re.sub(r"[^\d,]", "", value).replace(",", "."))
        return value


class LayoutChanged(RuntimeError):
    """O site mudou: um seletor que sempre funcionou não achou mais nada."""


def need(node, selector: str):
    found = node.select_one(selector)
    if found is None:
        raise LayoutChanged(f"o seletor {selector!r} não achou nada em <{node.name} data-id={node.get('data-id')}>")
    return found


def parse_catalog(html: str) -> list[Product]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("article.product")
    if not cards:
        raise LayoutChanged("nenhum 'article.product' encontrado")                        # falhe ALTO, não devolva lista vazia
    products = []
    for card in cards:
        stock = card.select_one(".stock")                                                 # este campo é opcional de verdade
        products.append(Product(
            id=card["data-id"],
            name=need(card, ".name").get_text(strip=True),
            price=need(card, ".price").get_text(),
            in_stock=bool(stock) and "out" not in stock.get("class", []),
        ))
    return products


html = httpx.get(BASE + "/catalog?page=1").text
products = parse_catalog(html)
print("válidos:", [(p.id, p.name, p.price, p.in_stock) for p in products[:2]], "...")

# 2. o site mudou uma classe CSS: o que acontece com cada estratégia?
changed = html.replace('class="price"', 'class="preco"')
for label, fn in [
    ("seletor direto, sem tratar", lambda: [c.select_one(".price").get_text() for c in BeautifulSoup(changed, "lxml").select("article.product")]),
    ("com need() e Pydantic", lambda: parse_catalog(changed)),
]:
    try:
        fn()
        print(f"  {label:<28} -> passou sem avisar")
    except Exception as error:
        print(f"  {label:<28} -> {type(error).__name__}: {str(error).splitlines()[0][:70]}")

# 3. dados ruins: coletar os erros de TODAS as linhas, em vez de parar na primeira
dirty = html.replace('<span class="price" itemprop="price" content="89.9">R$ 89,90</span>', '<span class="price">grátis</span>')
good, errors = [], []
for card in BeautifulSoup(dirty, "lxml").select("article.product"):
    try:
        good.append(Product(id=card["data-id"], name=card.select_one(".name").get_text(strip=True),
                            price=card.select_one(".price").get_text(), in_stock=True))
    except (ValidationError, ValueError) as error:
        errors.append((card["data-id"], type(error).__name__))
print(f"\nlinha ruim: {len(good)} válidas, {len(errors)} rejeitadas: {errors} (e o relatório diz qual)")

# 4. seletores estáveis: dados (data-*, itemprop, JSON-LD, aria) mudam menos que estilo (classes de layout)
soup = BeautifulSoup(html, "lxml")
by_style = soup.select("div > article > h2 > a")
by_data = soup.select("[data-id] [itemprop=name]")
print(f"\nseletor frágil (estrutura de layout): {len(by_style)} | seletor estável (atributos de dados): {len(by_data)}")

# 5. teste de contrato com uma página SALVA: o parser testa sem rede e rápido, e a falha mostra a mudança
saved = FIXTURES / "catalog-page1.html"
saved.write_text(html, encoding="utf-8")
print(f"\npágina salva ({saved.stat().st_size} bytes): parse offline -> {len(parse_catalog(saved.read_text(encoding='utf-8')))} produtos")

# 6. uma verificação periódica: compare a página de hoje com a salva (ex.: número de produtos e de campos)
def shape(page_html: str) -> dict:
    soup = BeautifulSoup(page_html, "lxml")
    return {"cards": len(soup.select("article.product")), "names": len(soup.select(".name")), "prices": len(soup.select(".price"))}


print("forma da página salva:", shape(saved.read_text(encoding="utf-8")), "| hoje:", shape(httpx.get(BASE + "/catalog?page=1").text),
      "| depois da mudança de layout:", shape(changed))
server.shutdown()
