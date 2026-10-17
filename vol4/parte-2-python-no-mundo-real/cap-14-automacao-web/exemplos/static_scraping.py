"""Raspagem estática: baixar HTML, achar os dados com seletores e transformá-los em tipos de verdade."""
import json
import re
import time
from html.parser import HTMLParser

import httpx
from bs4 import BeautifulSoup
from selectolax.lexbor import LexborHTMLParser as FastParser

import demo_site

server, BASE = demo_site.start()
client = httpx.Client(base_url=BASE, headers={"User-Agent": "curso-python-bot/1.0 (+contato@exemplo.com)"}, timeout=5)


def price_to_float(text: str) -> float:
    """'R$ 1.299,00' -> 1299.0: tira o símbolo, o ponto de milhar e troca a vírgula decimal."""
    return float(re.sub(r"[^\d,]", "", text).replace(",", "."))


# 1. baixar e olhar o HTML (o primeiro passo é SEMPRE olhar o que o servidor devolveu, não o que o navegador mostra)
response = client.get("/catalog", params={"page": 1})
print("status:", response.status_code, "| tipo:", response.headers["content-type"], "| bytes:", len(response.content))
html = response.text

# 2. BeautifulSoup + seletores CSS
soup = BeautifulSoup(html, "lxml")
print("\ntítulo:", soup.title.string, "| h1:", soup.select_one("h1").get_text(strip=True))
for card in soup.select("article.product")[:3]:
    link = card.select_one("h2.name a")
    print(" ", card["data-id"], link.get_text(strip=True), "|", card.select_one(".price").get_text(strip=True), "|", link["href"])

# 3. de texto para tipos: preço, estoque, esgotado
products = []
for card in soup.select("article.product"):
    stock_text = card.select_one(".stock").get_text(strip=True)
    products.append({
        "id": int(card["data-id"]),
        "name": card.select_one(".name").get_text(strip=True),
        "price": price_to_float(card.select_one(".price").get_text()),
        "price_meta": float(card.select_one("[itemprop=price]")["content"]),        # o microdado vale mais que o texto formatado
        "in_stock": "out" not in card.select_one(".stock")["class"],
    })
print("\nprodutos tipados:", products[:2])
print("preço do texto == preço do microdado?", all(p["price"] == p["price_meta"] for p in products))

# 4. paginação: seguir o link rel=next até acabar (e parar!)
def crawl_catalog():
    url, pages, items = "/catalog", 0, []
    while url and pages < 10:                                  # um limite de segurança: nunca confie no "next" infinito
        page = BeautifulSoup(client.get(url).text, "lxml")
        items += [c.select_one(".name").get_text(strip=True) for c in page.select("article.product")]
        nxt = page.select_one("a[rel=next]")
        url = nxt["href"] if nxt else None
        pages += 1
    return pages, items


pages, items = crawl_catalog()
print(f"\ncatálogo inteiro: {pages} páginas, {len(items)} produtos | primeiro: {items[0]} | último: {items[-1]}")

# 5. dados estruturados (JSON-LD) valem mais que o HTML: o site os escreve para as máquinas lerem
detail = BeautifulSoup(client.get("/product/3").text, "lxml")
ld = json.loads(detail.select_one('script[type="application/ld+json"]').string)
print("\nJSON-LD:", {"name": ld["name"], "sku": ld["sku"], "price": ld["offers"]["price"], "availability": ld["offers"]["availability"]})

# 6. HTML malformado: cada parser conserta de um jeito
broken = client.get("/broken").text
for parser in ("html.parser", "lxml"):
    tree = BeautifulSoup(broken, parser)
    print(f"{parser:<12} parágrafos: {len(tree.select('p.a'))} | itens: {[li.get_text(strip=True) for li in tree.select('li')]} | linhas de tabela: {len(tree.select('tr'))}")
fast = FastParser(broken)
print("selectolax   parágrafos:", len(fast.css("p.a")), "| itens:", [n.text(strip=True) for n in fast.css("li")], "| linhas de tabela:", len(fast.css("tr")))

# 7. três bibliotecas, um documento de 2,5 MB: o custo de parsear
big = "<html><body>" + "".join(
    f'<div class="row" id="r{i}"><a href="/p/{i}">item {i}</a><span class="price">R$ {i % 900 + 1},90</span></div>' for i in range(25_000)
) + "</body></html>"
print(f"\ndocumento de {len(big) / 1e6:.1f} MB, 25.000 linhas:")


def best(fn, repeat=3):
    out = []
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        out.append((time.perf_counter() - start) * 1e3)
    return min(out)


class Counter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.count = 0

    def handle_starttag(self, tag, attrs):
        if tag == "span" and ("class", "price") in attrs:
            self.count += 1


def stdlib():
    parser = Counter()
    parser.feed(big)
    return parser.count


results = [
    ("html.parser (stdlib)", lambda: stdlib()),
    ("BeautifulSoup + html.parser", lambda: len(BeautifulSoup(big, "html.parser").select("span.price"))),
    ("BeautifulSoup + lxml", lambda: len(BeautifulSoup(big, "lxml").select("span.price"))),
    ("lxml puro (XPath)", lambda: len(__import__("lxml.html", fromlist=["x"]).fromstring(big).xpath("//span[@class='price']"))),
    ("selectolax (Lexbor)", lambda: len(FastParser(big).css("span.price"))),
    ("regex (frágil!)", lambda: len(re.findall(r'<span class="price">', big))),
]
timed = []
for label, fn in results:
    count = fn()
    timed.append((label, best(fn, 2 if "Beautiful" in label else 3), count))
reference = next(ms for label, ms, _ in timed if label == "BeautifulSoup + lxml")
for label, ms, count in timed:
    print(f"  {label:<30} {ms:8.1f} ms | achou {count:,} | {reference / ms:6.1f}x o BeautifulSoup + lxml")

# 8. requests em um cliente com cabeçalhos honestos: o servidor vê quem você é
print("\nUser-Agent enviado:", client.get("/ua-only").text, "| httpx padrão:", httpx.get(BASE + "/ua-only").status_code, "(bloqueado: não se identificou)")
server.shutdown()
