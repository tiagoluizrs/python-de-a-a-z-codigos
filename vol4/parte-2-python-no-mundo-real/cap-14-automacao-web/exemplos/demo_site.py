"""Um "site de lojas" de brincadeira, 100% local, para raspar e automatizar SEM tocar a internet de ninguém.

Rotas:
  /robots.txt              regras (Disallow: /admin, Crawl-delay: 1)
  /catalog?page=N          lista de produtos em HTML (com paginação rel=next, microdados e JSON-LD)
  /product/<id>            página do produto (microdados e JSON-LD)
  /broken                  HTML malformado (tags sem fechar)
  /spa                     casca vazia; os produtos chegam por JavaScript (fetch em /api/products)
  /api/products?page=N     os mesmos produtos em JSON (o que o JavaScript chama)
  /form, /search           formulário de busca (GET) e a tabela de resultados
  /login, /account         login com cookie de sessão (usuário ana / senha 123)
  /download.csv            arquivo para baixar
  /flaky                   falha nas duas primeiras vezes por cliente (503), depois funciona
  /limited                 429 com Retry-After nas duas primeiras vezes
  /ua-only                 403 se o User-Agent não se identificar (contém "bot/")
  /etag                    suporta If-None-Match (304)
  /slow?ms=N               responde depois de N milissegundos
  /hits                    contador de requisições por caminho (JSON)
"""
import json
import threading
import time
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PRODUCTS = [
    {"id": i, "name": name, "price": price, "category": cat, "stock": stock}
    for i, (name, price, cat, stock) in enumerate([
        ("Teclado Mecânico", 349.90, "periféricos", 12), ("Mouse Sem Fio", 89.90, "periféricos", 40),
        ("Monitor 27 polegadas", 1299.00, "monitores", 5), ("Webcam Full HD", 219.50, "periféricos", 0),
        ("Cabo HDMI 2m", 29.90, "acessórios", 200), ("Suporte de Notebook", 119.00, "acessórios", 33),
        ("Headset Gamer", 259.90, "áudio", 18), ("Caixa de Som Bluetooth", 179.90, "áudio", 25),
        ("SSD 1 TB", 459.00, "armazenamento", 60), ("HD Externo 2 TB", 549.00, "armazenamento", 14),
        ("Hub USB-C", 139.90, "acessórios", 77), ("Mousepad Grande", 49.90, "acessórios", 90),
        ("Microfone USB", 329.00, "áudio", 9), ("Monitor 24 polegadas", 899.00, "monitores", 21),
        ("Cadeira Ergonômica", 1599.00, "móveis", 4), ("Luminária de Mesa", 99.90, "móveis", 52),
    ], start=1)
]
PER_PAGE = 5
HITS: Counter = Counter()
CLIENT_FAILS: Counter = Counter()
SESSIONS: set[str] = set()
LOCK = threading.Lock()


def brl(value: float) -> str:
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def page_of(n: int):
    start = (n - 1) * PER_PAGE
    return PRODUCTS[start:start + PER_PAGE]


def last_page() -> int:
    return -(-len(PRODUCTS) // PER_PAGE)


def card(p) -> str:
    return (f'<article class="product" data-id="{p["id"]}" itemscope itemtype="https://schema.org/Product">'
            f'<h2 class="name" itemprop="name"><a href="/product/{p["id"]}">{p["name"]}</a></h2>'
            f'<span class="price" itemprop="price" content="{p["price"]}">{brl(p["price"])}</span>'
            f'<span class="category">{p["category"]}</span>'
            f'<span class="stock {"out" if p["stock"] == 0 else "in"}">{"Esgotado" if p["stock"] == 0 else str(p["stock"]) + " em estoque"}</span>'
            f'</article>')


def layout(title: str, body: str, head: str = "") -> bytes:
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{title}</title>{head}</head>'
            f'<body><nav><a href="/">início</a> | <a href="/catalog">catálogo</a> | <a href="/spa">SPA</a> | <a href="/form">busca</a></nav>'
            f'{body}</body></html>').encode()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "DemoSite/1.0"

    def log_message(self, *args):
        pass

    def send(self, status=200, body=b"", ctype="text/html; charset=utf-8", headers=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def client_key(self) -> str:
        return self.headers.get("X-Client", self.client_address[0])

    def cookies(self) -> dict:
        jar = {}
        for part in self.headers.get("Cookie", "").split(";"):
            if "=" in part:
                key, value = part.strip().split("=", 1)
                jar[key] = value
        return jar

    def do_GET(self):
        url = urlparse(self.path)
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        with LOCK:
            HITS[url.path] += 1
        path = url.path
        if path == "/":
            self.send(body=layout("Loja Demo", "<h1>Loja Demo</h1><p>Um site local para praticar raspagem.</p>"))
        elif path == "/robots.txt":
            self.send(body=b"User-agent: *\nDisallow: /admin\nDisallow: /account\nCrawl-delay: 1\n\nUser-agent: badbot\nDisallow: /\n",
                      ctype="text/plain; charset=utf-8")
        elif path == "/catalog":
            n = max(1, int(query.get("page", 1)))
            if n > last_page():
                return self.send(404, layout("404", "<h1>Sem página</h1>"))
            nav = (f'<link rel="prev" href="/catalog?page={n - 1}">' if n > 1 else "") + (f'<link rel="next" href="/catalog?page={n + 1}">' if n < last_page() else "")
            body = f'<h1>Catálogo</h1><section id="list">{"".join(card(p) for p in page_of(n))}</section>'
            body += f'<a class="next" rel="next" href="/catalog?page={n + 1}">Próxima</a>' if n < last_page() else ""
            self.send(body=layout(f"Catálogo, página {n}", body, nav))
        elif path.startswith("/product/"):
            pid = int(path.rsplit("/", 1)[1])
            p = next((x for x in PRODUCTS if x["id"] == pid), None)
            if not p:
                return self.send(404, layout("404", "<h1>Produto não encontrado</h1>"))
            ld = json.dumps({"@context": "https://schema.org", "@type": "Product", "name": p["name"], "sku": f"SKU-{pid:04d}",
                             "offers": {"@type": "Offer", "price": p["price"], "priceCurrency": "BRL",
                                        "availability": "InStock" if p["stock"] else "OutOfStock"}}, ensure_ascii=False)
            self.send(body=layout(p["name"], card(p) + f"<p class=\"desc\">Descrição de {p['name']}.</p>", f'<script type="application/ld+json">{ld}</script>'))
        elif path == "/broken":
            self.send(body="<html><body><h1>Sem fechar<p class=a>um<p class=a>dois<ul><li>x<li>y</ul><b>negrito<i>itálico</b></i><table><tr><td>1<td>2<tr><td>3".encode())
        elif path == "/spa":
            script = """<script>
              let page = 1;
              async function load() {
                const r = await fetch('/api/products?page=' + page);
                const data = await r.json();
                const list = document.getElementById('list');
                for (const p of data.items) {
                  const el = document.createElement('article'); el.className = 'product'; el.dataset.id = p.id;
                  el.innerHTML = `<h2 class="name">${p.name}</h2><span class="price">R$ ${p.price.toFixed(2)}</span>`;
                  list.appendChild(el);
                }
                page += 1;
                if (!data.has_more) document.getElementById('more').remove();
              }
              setTimeout(load, 300);
              document.getElementById('more').addEventListener('click', load);
            </script>"""
            self.send(body=layout("SPA", '<h1>Catálogo dinâmico</h1><div id="list"></div><button id="more">Carregar mais</button>' + script))
        elif path == "/api/products":
            n = max(1, int(query.get("page", 1)))
            items = page_of(n)
            self.send(body=json.dumps({"page": n, "items": items, "has_more": n < last_page()}).encode(), ctype="application/json")
        elif path == "/form":
            self.send(body=layout("Busca", '<h1>Buscar</h1><form action="/search" method="get"><label>Termo <input name="q" id="q"></label>'
                                           '<label>Categoria <select name="category" id="category"><option value="">todas</option><option>periféricos</option>'
                                           '<option>monitores</option><option>áudio</option><option>acessórios</option></select></label>'
                                           '<label><input type="checkbox" name="in_stock" id="in_stock" value="1"> só em estoque</label>'
                                           '<button type="submit">Buscar</button></form>'))
        elif path == "/search":
            q = query.get("q", "").lower()
            rows = [p for p in PRODUCTS if q in p["name"].lower() and (not query.get("category") or p["category"] == query["category"])
                    and (not query.get("in_stock") or p["stock"] > 0)]
            table = "".join(f'<tr><td>{p["id"]}</td><td>{p["name"]}</td><td>{brl(p["price"])}</td></tr>' for p in rows)
            self.send(body=layout("Resultados", f'<h1>Resultados</h1><p id="count">{len(rows)} resultado(s)</p><table id="results"><thead><tr><th>ID</th><th>Nome</th><th>Preço</th></tr></thead><tbody>{table}</tbody></table>'))
        elif path == "/login":
            self.send(body=layout("Entrar", '<h1>Entrar</h1><form action="/login" method="post"><input name="user" id="user"><input name="password" id="password" type="password"><button>Entrar</button></form>'))
        elif path == "/account":
            token = self.cookies().get("session")
            if token in SESSIONS:
                self.send(body=layout("Conta", '<h1>Minha conta</h1><p id="welcome">Olá, ana!</p><a id="export" href="/download.csv">Exportar pedidos</a>'))
            else:
                self.send(302, b"", headers={"Location": "/login"})
        elif path == "/download.csv":
            csv = "id,name,price\n" + "\n".join(f'{p["id"]},{p["name"]},{p["price"]}' for p in PRODUCTS[:5]) + "\n"
            self.send(body=csv.encode(), ctype="text/csv; charset=utf-8", headers={"Content-Disposition": 'attachment; filename="produtos.csv"'})
        elif path == "/flaky":
            with LOCK:
                CLIENT_FAILS[("flaky", self.client_key())] += 1
                count = CLIENT_FAILS[("flaky", self.client_key())]
            self.send(503 if count <= 2 else 200, b"tente de novo" if count <= 2 else b"ok", ctype="text/plain")
        elif path == "/limited":
            with LOCK:
                CLIENT_FAILS[("limited", self.client_key())] += 1
                count = CLIENT_FAILS[("limited", self.client_key())]
            if count <= 2:
                self.send(429, b"devagar", ctype="text/plain", headers={"Retry-After": "1"})
            else:
                self.send(200, b"ok", ctype="text/plain")
        elif path == "/ua-only":
            if "bot/" in self.headers.get("User-Agent", ""):
                self.send(200, b"identificado", ctype="text/plain")
            else:
                self.send(403, b"identifique-se", ctype="text/plain")
        elif path == "/etag":
            etag = '"v1"'
            if self.headers.get("If-None-Match") == etag:
                self.send(304, b"", headers={"ETag": etag})
            else:
                self.send(200, b"conteudo grande " * 1000, ctype="text/plain", headers={"ETag": etag})
        elif path == "/slow":
            time.sleep(int(query.get("ms", 200)) / 1000)
            self.send(200, b"devagar", ctype="text/plain")
        elif path == "/hits":
            self.send(body=json.dumps(dict(HITS)).encode(), ctype="application/json")
        else:
            self.send(404, layout("404", "<h1>Não encontrado</h1>"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        form = {k: v[0] for k, v in parse_qs(self.rfile.read(length).decode()).items()}
        if self.path == "/login" and form.get("user") == "ana" and form.get("password") == "123":
            token = f"tok-{len(SESSIONS) + 1}"
            SESSIONS.add(token)
            self.send(302, b"", headers={"Location": "/account", "Set-Cookie": f"session={token}; Path=/; HttpOnly"})
        else:
            self.send(401, layout("Erro", '<p id="error">Usuário ou senha inválidos</p>'))

    def handle_error(self, request, client_address):
        pass


class QuietServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass


def start(port: int = 0) -> tuple[ThreadingHTTPServer, str]:
    """Sobe o servidor em uma thread e devolve ``(servidor, url_base)``."""
    server = QuietServer(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"


def reset() -> None:
    with LOCK:
        HITS.clear()
        CLIENT_FAILS.clear()
        SESSIONS.clear()


if __name__ == "__main__":
    server, base = start(8765)
    print("site de demonstração em", base, "(Ctrl+C para parar)")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        server.shutdown()
