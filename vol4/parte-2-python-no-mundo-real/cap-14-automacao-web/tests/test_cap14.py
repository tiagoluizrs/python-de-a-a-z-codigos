import pytest

import demo_site

CATALOG = """<html><body><section>
<article class="product" data-id="7" itemscope><h2 class="name"> <a href="/product/7">Teclado Mecânico </a></h2>
 <span class="price" itemprop="price" content="349.9">R$ 349,90</span><span class="category">periféricos</span><span class="stock in">12 em estoque</span></article>
<article class="product" data-id="8"><h2 class="name">Monitor</h2><span class="price">R$ 1.299,00</span><span class="stock out">Esgotado</span></article>
<article class="product" data-id="9"><h2 class="name">Cabo</h2><span class="price">R$ 9,90</span></article>
</section></body></html>"""


# ---------- ex01 ----------
def test_parse_products(load_exercise):
    m = load_exercise("ex01_parse_catalog")
    products = m.parse_products(CATALOG)
    assert [p["id"] for p in products] == [7, 8, 9]
    assert products[0] == {"id": 7, "name": "Teclado Mecânico", "price": 349.9, "category": "periféricos", "stock": 12, "in_stock": True}
    assert products[1]["price"] == 1299.0 and products[1]["stock"] == 0 and products[1]["in_stock"] is False and products[1]["category"] is None
    assert products[2]["stock"] is None and products[2]["in_stock"] is False and products[2]["price"] == 9.9


def test_parse_products_layout_changed(load_exercise):
    m = load_exercise("ex01_parse_catalog")
    with pytest.raises(ValueError, match="layout mudou"):
        m.parse_products("<html><body><div class='item'>x</div></body></html>")


def test_parse_products_against_demo_site(load_exercise):
    import httpx
    m = load_exercise("ex01_parse_catalog")
    server, base = demo_site.start()
    try:
        products = m.parse_products(httpx.get(base + "/catalog?page=1").text)
    finally:
        server.shutdown()
    assert len(products) == 5 and products[2]["price"] == 1299.0 and products[0]["name"] == "Teclado Mecânico"
    assert all(isinstance(p["stock"], int) for p in products)


# ---------- ex02 ----------
def make_fetch(pages):
    calls = []

    def fetch(url):
        calls.append(url)
        return pages.get(url)

    fetch.calls = calls
    return fetch


def page(names, next_href=None):
    body = "".join(f'<h2 class="name">{n}</h2>' for n in names)
    link = f'<a rel="next" href="{next_href}">próxima</a>' if next_href else ""
    return f"<html><body>{body}{link}</body></html>"


def test_crawl_follows_next_with_relative_links(load_exercise):
    m = load_exercise("ex02_crawl")
    fetch = make_fetch({
        "http://s/catalog?page=1": page(["a", "b"], "/catalog?page=2"),
        "http://s/catalog?page=2": page(["c"], "?page=3"),
        "http://s/catalog?page=3": page(["d", "e"]),
    })
    urls, items = m.crawl(fetch, "http://s/catalog?page=1")
    assert urls == ["http://s/catalog?page=1", "http://s/catalog?page=2", "http://s/catalog?page=3"]
    assert items == ["a", "b", "c", "d", "e"] and fetch.calls == urls


def test_crawl_stops_on_loop_missing_page_and_limit(load_exercise):
    m = load_exercise("ex02_crawl")
    loop = make_fetch({"http://s/1": page(["a"], "/2"), "http://s/2": page(["b"], "/1")})
    urls, items = m.crawl(loop, "http://s/1")
    assert urls == ["http://s/1", "http://s/2"] and items == ["a", "b"] and len(loop.calls) == 2
    missing = make_fetch({"http://s/1": page(["a"], "/gone")})
    urls, items = m.crawl(missing, "http://s/1")
    assert urls == ["http://s/1"] and items == ["a"] and missing.calls == ["http://s/1", "http://s/gone"]
    chain = make_fetch({f"http://s/{i}": page([str(i)], f"/{i + 1}") for i in range(1, 100)})
    urls, items = m.crawl(chain, "http://s/1", max_pages=4)
    assert len(urls) == 4 and items == ["1", "2", "3", "4"] and len(chain.calls) == 4


# ---------- ex03 ----------
ROBOTS = "User-agent: *\nDisallow: /admin\nDisallow: /account\nCrawl-delay: 2\n\nUser-agent: fastbot\nCrawl-delay: 1\n\nUser-agent: badbot\nDisallow: /\n"


def test_robots_allowed(load_exercise):
    m = load_exercise("ex03_robots")
    robots = m.Robots(ROBOTS, "curso-bot")
    assert robots.allowed("http://s/catalog?page=2") and robots.allowed("http://s/product/3")
    assert not robots.allowed("http://s/admin") and not robots.allowed("http://s/account/orders")
    assert not m.Robots(ROBOTS, "badbot").allowed("http://s/catalog")


def test_robots_delay_never_below_default(load_exercise):
    m = load_exercise("ex03_robots")
    assert m.Robots(ROBOTS, "curso-bot").delay() == 2.0
    assert m.Robots(ROBOTS, "fastbot").delay() == 1.0
    assert m.Robots(ROBOTS, "fastbot", default_delay=3).delay() == 3.0              # o site aceita 1 s, mas o nosso mínimo é 3 s
    assert m.Robots(ROBOTS, "fastbot", default_delay=0.1).delay() == 1.0
    assert m.Robots("User-agent: *\nDisallow:\n", "x").delay() == 1.0
    assert m.Robots("User-agent: *\nDisallow:\n", "x", default_delay=3).delay() == 3.0


def test_robots_filter_urls(load_exercise):
    m = load_exercise("ex03_robots")
    robots = m.Robots(ROBOTS, "curso-bot")
    urls = ["http://s/a", "http://s/admin/x", "http://s/b", "http://s/account"]
    assert robots.filter_urls(urls) == (["http://s/a", "http://s/b"], ["http://s/admin/x", "http://s/account"])


# ---------- ex04 ----------
def scripted(responses):
    seq = iter(responses)
    calls = []

    def get(url):
        calls.append(url)
        return next(seq)

    get.calls = calls
    return get


def test_retry_success_after_failures(load_exercise):
    m = load_exercise("ex04_retry")
    sleeps = []
    get = scripted([(503, {}, "x"), (500, {}, "x"), (200, {}, "ok")])
    assert m.get_with_backoff(get, "http://s/", sleeps.append) == "ok"
    assert sleeps == [0.5, 1.0] and len(get.calls) == 3


def test_retry_honors_retry_after_and_cap(load_exercise):
    m = load_exercise("ex04_retry")
    sleeps = []
    get = scripted([(429, {"retry-after": "3"}, ""), (429, {"retry-after": "20"}, ""), (503, {}, ""), (200, {}, "ok")])
    assert m.get_with_backoff(get, "u", sleeps.append, max_attempts=5, cap=1.0) == "ok"
    assert sleeps == [3.0, 20.0, 1.0]                                    # o Retry-After manda mesmo acima do teto; o backoff respeita o teto
    sleeps.clear()
    get = scripted([(502, {}, "")] * 6 + [(200, {}, "ok")])
    m.get_with_backoff(get, "u", sleeps.append, max_attempts=7, base=1.0, cap=4.0)
    assert sleeps == [1.0, 2.0, 4.0, 4.0, 4.0, 4.0]


def test_retry_client_errors_do_not_retry(load_exercise):
    m = load_exercise("ex04_retry")
    sleeps = []
    for status in (400, 403, 404):
        get = scripted([(status, {}, "nope")])
        assert m.get_with_backoff(get, "u", sleeps.append) == "nope"
        assert len(get.calls) == 1
    assert sleeps == []


def test_retry_gives_up(load_exercise):
    m = load_exercise("ex04_retry")
    sleeps = []
    get = scripted([(503, {}, "")] * 3)
    with pytest.raises(m.GaveUp, match=r"desistindo de http://s/x após 3 tentativas \(último status: 503\)"):
        m.get_with_backoff(get, "http://s/x", sleeps.append, max_attempts=3)
    assert len(sleeps) == 2 and len(get.calls) == 3                      # não dorme depois da última


# ---------- ex05 ----------
LD_PAGE = """<html><head>
<script type="application/ld+json">{"@type": "Product", "name": "A", "sku": "S1", "offers": {"price": "1299.00", "priceCurrency": "BRL", "availability": "https://schema.org/InStock"}}</script>
<script type="application/ld+json">[{"@type": "Organization", "name": "Loja"}, 42, {"@type": ["Thing", "Product"], "name": "B", "offers": [{"price": 5, "availability": "OutOfStock"}]}]</script>
<script type="application/ld+json">{ isso não é json }</script>
<script type="application/ld+json"></script>
<script type="application/ld+json">{"@context": "x", "@graph": [{"@type": "Product", "name": "C"}, {"@type": "WebSite"}, "texto"]}</script>
</head><body></body></html>"""


def test_extract_jsonld(load_exercise):
    m = load_exercise("ex05_jsonld")
    items = m.extract_jsonld(LD_PAGE)
    assert [i.get("name") for i in items] == ["A", "Loja", "B", "C", None]
    assert items[-1]["@type"] == "WebSite"
    assert m.extract_jsonld("<html><body>nada</body></html>") == []


def test_products_summary(load_exercise):
    m = load_exercise("ex05_jsonld")
    assert m.products_summary(LD_PAGE) == [
        {"name": "A", "sku": "S1", "price": 1299.0, "currency": "BRL", "available": True},
        {"name": "B", "sku": None, "price": 5.0, "currency": None, "available": False},
        {"name": "C", "sku": None, "price": None, "currency": None, "available": False},
    ]


def test_jsonld_from_demo_site(load_exercise):
    import httpx
    m = load_exercise("ex05_jsonld")
    server, base = demo_site.start()
    try:
        summary = m.products_summary(httpx.get(base + "/product/3").text)
    finally:
        server.shutdown()
    assert summary == [{"name": "Monitor 27 polegadas", "sku": "SKU-0003", "price": 1299.0, "currency": "BRL", "available": True}]


# ---------- ex06 (precisa do Chromium) ----------
@pytest.fixture(scope="module")
def browser():
    sync_api = pytest.importorskip("playwright.sync_api")
    pw = sync_api.sync_playwright().start()
    try:
        browser = pw.chromium.launch()
    except Exception as error:                                           # navegador não instalado
        pw.stop()
        pytest.skip(f"Chromium indisponível: {str(error).splitlines()[0]}")
    yield browser
    browser.close()
    pw.stop()


@pytest.fixture
def page_(browser):
    page = browser.new_page()
    yield page
    page.close()


LOAD_MORE = """<div id="list"></div><button id="more">mais</button><script>
let n = 0;
function load() { setTimeout(() => {
  for (let i = 0; i < 3; i++) { const el = document.createElement('li'); el.className = 'it'; el.textContent = 'item ' + (++n); document.getElementById('list').appendChild(el); }
  if (n >= 7) document.getElementById('more').remove();
}, 150); }
setTimeout(load, 200);
document.getElementById('more').addEventListener('click', load);
</script>"""


def test_load_all(load_exercise, page_):
    m = load_exercise("ex06_dynamic")
    page_.set_content(LOAD_MORE)
    assert m.load_all(page_, ".it", "#more") == [f"item {i}" for i in range(1, 10)]


TABLE = """<table id="t"><thead><tr><th> Nome </th><th>Qtd</th></tr></thead><tbody></tbody></table><script>
setTimeout(() => { document.querySelector('#t tbody').innerHTML = '<tr><td>a</td><td> 1 </td></tr><tr><td>b</td><td>2</td></tr>'; }, 300);
</script>"""


def test_read_table_waits_for_javascript(load_exercise, page_):
    m = load_exercise("ex06_dynamic")
    page_.set_content(TABLE)
    assert m.read_table(page_, "#t") == [{"Nome": "a", "Qtd": "1"}, {"Nome": "b", "Qtd": "2"}]


def test_read_table_empty(load_exercise, page_):
    m = load_exercise("ex06_dynamic")
    page_.set_content('<table id="t"><thead><tr><th>x</th></tr></thead><tbody></tbody></table>')
    with pytest.raises(ValueError, match="tabela vazia"):
        m.read_table(page_, "#t")


def test_fill_and_submit_against_demo_site(load_exercise, page_):
    m = load_exercise("ex06_dynamic")
    server, base = demo_site.start()
    try:
        page_.goto(base + "/form")
        page_.evaluate("document.querySelector('form').insertAdjacentHTML('beforeend', '')")
        page_.evaluate("document.querySelector('button').setAttribute('type', 'submit')")
        m.fill_and_submit(page_, {"q": "monitor", "category": "monitores"})
        assert "/search?q=monitor&category=monitores" in page_.url
        assert page_.locator("#count").inner_text() == "2 resultado(s)"
    finally:
        server.shutdown()
